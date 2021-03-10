# git inventory plugin
# Read YAML variable files and aggregte them into host group variables
# With vaulted variable support
from __future__ import (absolute_import, division, print_function)
import argparse
import copy
import configparser
from distutils.util import strtobool
import getpass
import git
import giturlparse
import json
import os
import re
import sys
import time
import yaml
from shutil import rmtree
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.plugins.inventory import BaseInventoryPlugin

__metaclass__ = type

NoneType = type(None)

DOCUMENTATION = '''
    name: spatiumcepa.platform.git
    version_added: "2.10"
    short_description: Clone and read git repo YAML files as inventory source with Ansible Vault variable tag support
    description:
        - git repository will be checked out, and cached
        - arbitrary YAML files can define ansible variables, host groups, and include other files that do the same
    notes:
        - !vault inline encrypted variables will NOT be decrypted, allowing it to be done at playbook run time instead of during inventory aggregation
    options:
        plugin:
            description: indicates this is a configuration of the spatiumcepa.platform.git plugin
            required: true
            choices: ['spatiumcepa.platform.git']
        file_path:
            description: File path to git inventory to read
        ssh_key:
            description: Path to SSH identity file to use for git operations such as GIT_SSH_COMMAND=ssh -i SSH_KEY
        git_url:
            description: Git URL to clone for inventory configuration
        commit:
            description: Git commit, branch, or tag to check out
            default: master
        git_repo_cache_dir:
            description: Where to store the repository clones
        git_repo_cache_update_time_seconds:
            description: How old should the repo cache get before being refreshed
            type: int
            default: 3600
        delete_repo_cache:
            description: Should the repository cache be deleted before cloning any repositories?
            type: bool
            default: False
'''

EXAMPLES = '''# fmt: yaml
---
plugin: spatiumcepa.platform.git

git_url: git@github.com:spatium-cepa/customer-configuration.git
commit: master
file_path: platforms/cloud.yml
delete_repo_cache: false
# load working copy file without checking out git repo by only specifying file path
# file_path: /home/nkiraly/src/spatium-cepa/customer-configuration/platforms/cloud.yml
'''


class InventoryModule(BaseInventoryPlugin):  # TODO: implement Cacheable

    NAME = 'spatiumcepa.platform.git'

    ANSIBLE_INVENTORY_GIT_HOST_TYPE = '_aig_type'

    def __init__(self):

        super(InventoryModule, self).__init__()

        self._options = {}
        self._vars = {}

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('git.yaml', 'git.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        ''' Populates inventory from the given data. Raises an error on any parse failure
            :arg inventory: a copy of the previously accumulated inventory data,
                 to be updated with any new data this plugin provides.
                 The inventory can be empty if no other source/plugin ran successfully.
            :arg loader: a reference to the DataLoader, which can read in YAML and JSON files,
                 it also has Vault support to automatically decrypt files.
            :arg path: the string that represents the 'inventory source',
                 normally a path to a configuration file for this inventory,
                 but it can also be a raw string for this plugin to consume
            :arg cache: a boolean that indicates if the plugin should use the cache or not
                 you can ignore if this plugin does not implement caching.
        '''

        self.inventory = inventory
        self.loader = loader

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(self.inventory, self.loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        config = self._read_config_data(path)

        self.debug = False
        self._git_repo_path = None

        self.log("start processing options")
        self.ssh_key = self.get_option('ssh_key')
        self.git_url = self.get_option('git_url')
        self.commit = self.get_option('commit')
        self.file_path = self.get_option('file_path')
        self.delete_repo_cache = self.get_option('delete_repo_cache')
        self._current_user = getpass.getuser()
        self.git_repo_cache_dir = '/tmp/' + self._current_user + '-ansible-inventory-git-cache'
        self.log(f"parse trace 1 git_repo_cache_dir={self.git_repo_cache_dir}")
        if self.get_option('git_repo_cache_dir') is not None:
            self.git_repo_cache_dir = self.get_option('git_repo_cache_dir')
        self.git_repo_cache_update_time_seconds = self.get_option('git_repo_cache_update_time_seconds')
        self.log("finish processing options")

        # by default, use local file_path
        inventory_file_path = self.file_path

        # if git_url specified, check out the repo and use file_path in repo check out
        if self.git_url is not None:
            self.log(f"git_url is {self.git_url}")
            self._update_repository()
            inventory_file_path = os.path.join(self._git_repo_path, self.file_path)
            if not os.path.isfile(inventory_file_path):
                raise IOError(f"Inventory file '{self.file_path}' not found in repository at {inventory_file_path}")

        inventory_name = os.path.basename(inventory_file_path).split('.')[0]

        # initialize inventory dictionary to populate to spec minimum
        inventory_yaml_dict = {}

        inventory_tree = self._read_inventory_file(inventory_file_path)
        self.log("start building inventory")
        inventory_yaml_dict = self._build_inventory(
            inventory_file_path=inventory_file_path,
            inventory=inventory_yaml_dict,
            parent=inventory_tree,
            parent_name=inventory_name
        )
        self.log("finish building inventory")
        self.log(self._yaml_format_dict(inventory_yaml_dict))

        # TODO: flag parse yaml dict modality ?
        # where builder code does add_host / add_child / set_variable directly ?
        # will this break vault encrypted variables?
        if True:
            if isinstance(inventory_yaml_dict, MutableMapping):
                for group_name in inventory_yaml_dict:
                    self._parse_group(group_name, inventory_yaml_dict[group_name])
            else:
                raise AnsibleParserError("Invalid inventory data, expected dictionary and got:\n\n%s" % to_native(data))

    def log(self, msg):
        # TODO: self.display.vvvv why u no?
        if self.debug:
            fh = open("git-inventory.log", "a")
            fh.write(msg + u'\n')
            fh.close()

    def clean_cache(self):
        # remove repository directory if delete flag is set
        if self.delete_repo_cache and os.path.isdir(self._git_repo_path):
            self.log("Cleaning repository cache at {self._git_repo_path}")
            rmtree(self._git_repo_path)

    def _update_repository(self):
        self.log("enter _update_repository")
        if self.ssh_key:
            os.environ['GIT_SSH_COMMAND'] = 'ssh -i ' + self.ssh_key

        git_url_info = giturlparse.parse(self.git_url)
        git_repo_name = git_url_info.name

        self.log(f"setting _git_repo_path git_repo_cache_dir={self.git_repo_cache_dir} git_repo_name={git_repo_name}")
        self._git_repo_path = os.path.join(self.git_repo_cache_dir, git_repo_name)
        self.log(f"_git_repo_path = {self._git_repo_path}")
        git_repo_git_dir_path = os.path.join(self._git_repo_path, '.git')

        if self.delete_repo_cache:
            self.log(f"Ensuring repository cache clean before clone {self._git_repo_path}")
            self.clean_cache()

        if not os.path.exists(self._git_repo_path):
            self.log(f"Cloning repository {self._git_repo_path}. Cache clone directory {self._git_repo_path} does not exist.")
            repo = git.Repo.clone_from(self.git_url, self._git_repo_path)
        else:
            self.log(f"Using repository found at {self._git_repo_path}")
            repo = git.Repo(self._git_repo_path)
            # check for recently updated to prevent unnecessary checkouts
            repo_git_dir_mtime = os.path.getmtime(git_repo_git_dir_path)
            repo_git_dir_mtime_age = time.time() - repo_git_dir_mtime
            if repo_git_dir_mtime_age < self.git_repo_cache_update_time_seconds:
                self.log(
                    f"Skipping repository update: last modified {repo_git_dir_mtime_age} seconds ago while threshold is {self.git_repo_cache_update_time_seconds}")
                return

            # Checking out the master branch ensures that we will not be in a detached head state when we pull to update
            self.log('Checking out repository master')
            repo.git.checkout("master")

            self.log('Pulling repository remote origin')
            repo.remotes.origin.pull()

            self.log('Updating .git dir modified time to now')
            now_time = time.time()
            os.utime(git_repo_git_dir_path, (now_time, now_time))

        self.log(f"Checking out repository commit {self.commit}")
        repo.git.checkout(self.commit)

    def _read_inventory_file(self, inventory_file_path):
        self.log(f"Reading inventory file {inventory_file_path}")
        with open(inventory_file_path, 'r') as ifh:
            inventory_tree = yaml.load(ifh, Loader=yaml.SafeLoader)
            return inventory_tree

    def _read_variable_file(self, variable_file_path):
        self.log(f"Reading variable file {variable_file_path}")
        dl = DataLoader()
        variable_tree = dl.load_from_file(variable_file_path)
        return variable_tree

    def _build_inventory(self, inventory_file_path, inventory, parent, parent_name):
        self.log(f"Build inventory from inventory_file_path {inventory_file_path}\n parent {parent_name} = {json.dumps(parent)}")

        # build host group
        inventory[parent_name] = {
            'children': []
        }
        for child_name, child in parent.items():
            if child is None:
                # when child is None,
                # make it a host group in this group only
                if 'children' not in inventory[parent_name]:
                    inventory[parent_name]['children'] = []
                inventory[parent_name]['children'].append(child_name)
                # only type: host declarations are ansible inventory hosts - see next case
            # if type is host, put host and its variables in hosts entry for the parent
            elif self.ANSIBLE_INVENTORY_GIT_HOST_TYPE in child and child[self.ANSIBLE_INVENTORY_GIT_HOST_TYPE] == 'host':
                self.log("adding child host type to parent")
                # put host in list of hosts in the group
                if 'hosts' not in inventory[parent_name]:
                    inventory[parent_name]['hosts'] = dict()
                inventory[parent_name]['hosts'][child_name] = None
                # update host entry with vars if any are defined
                # hosts are different where vars are defined in a dict that is specified as the value of the host node
                # https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html#tuning-the-external-inventory-script
                if 'vars' in child:
                    if inventory[parent_name]['hosts'][child_name] == None:
                        inventory[parent_name]['hosts'][child_name] = {}
                    inventory[parent_name]['hosts'][child_name].update(child['vars'])
            elif child_name == 'vars':
                self.log(f"{parent_name} vars child found")
                # child is variables for this host group
                host_group_vars = {}
                if 'vars' in inventory[parent_name]:
                    self.log(f"existing vars found in {parent_name}")
                    host_group_vars = copy.deepcopy(inventory[parent_name]['vars'])
                host_group_vars.update(child)
                inventory[parent_name]['vars'] = host_group_vars
            elif child_name == 'includes':
                # child is include file list to add to this host group
                for include_file in child:
                    include_file_path = os.path.join(os.path.dirname(inventory_file_path), include_file)
                    self.log(f"{parent_name} parents include file {include_file_path}")
                    include_inventory_tree = self._read_inventory_file(include_file_path)
                    include_inventory_name = os.path.basename(include_file_path).split('.')[0]
                    if 'children' not in inventory[parent_name]:
                        inventory[parent_name]['children'] = []
                    inventory[parent_name]['children'].append(include_inventory_name)
                    inventory = self._build_inventory(inventory_file_path=include_file_path, inventory=inventory,
                                                      parent=include_inventory_tree, parent_name=include_inventory_name)
            elif child_name == 'include_vars':
                # child is include variable file list to add to this host group
                for include_var_file in child:
                    include_var_file_path = os.path.join(os.path.dirname(inventory_file_path), include_var_file)
                    self.log(f"{parent_name} includes var file {include_var_file_path}")
                    include_variable_tree = self._read_variable_file(include_var_file_path)
                    # add variables to parent host group variables
                    host_group_vars = {}
                    if 'vars' in inventory[parent_name]:
                        self.log(f"existing vars found in {parent_name}")
                        host_group_vars = copy.deepcopy(inventory[parent_name]['vars'])
                    host_group_vars.update(include_variable_tree)
                    inventory[parent_name]['vars'] = host_group_vars
            else:
                # else, add child to current group
                if 'children' not in inventory[parent_name]:
                    inventory[parent_name]['children'] = []
                inventory[parent_name]['children'].append(child_name)
                # process child host group
                self.log(f"recursing into child host group {child_name}")
                inventory = self._build_inventory(inventory_file_path=inventory_file_path,
                                                  inventory=inventory, parent=child, parent_name=child_name)

        return inventory

    def _json_format_dict(self, inventory, pretty=False):
        # convert inventory dictionary to json string
        if pretty:
            return json.dumps(inventory, sort_keys=True, indent=2)
        else:
            return json.dumps(inventory)

    def _yaml_format_dict(self, inventory, default_flow_style=False):
        # convert inventory dictionary to yaml string
        return yaml.dump(inventory, Dumper=AnsibleDumper, default_flow_style=default_flow_style).replace('null', '')

    def _find_host_vars(self, host, inventory):
        # per ansible inventory spec, default host vars is empty dictionary
        host_vars = dict()
        if len(inventory) == 0:
            return host_vars

        for group_name, host_group in inventory.iteritems():
            host_match = False
            # if the host group name matches or a host in this group matches
            if group_name == host:
                host_match = True

            if 'hosts' in host_group:
                # TODO: host pattern matching?
                if host in host_group['hosts']:
                    host_match = True

            if 'vars' in host_group and host_match:
                # add this host group vars to the variables to return
                host_vars.update(host_group['vars'])

        return host_vars

    def _parse_group(self, group, group_data):

        if isinstance(group_data, (MutableMapping, NoneType)):

            try:
                group = self.inventory.add_group(group)
            except AnsibleError as e:
                raise AnsibleParserError("Unable to add group %s: %s" % (group, to_text(e)))

            if group_data is not None:
                # make sure they are dicts
                for section in ['vars', 'children', 'hosts']:
                    if section in group_data:
                        # convert strings to dicts as these are allowed
                        if isinstance(group_data[section], string_types):
                            group_data[section] = {group_data[section]: None}

                        # convert list to dictionary to make it a mutable mapping
                        if isinstance(group_data[section], list):
                            group_data[section] = dict.fromkeys(group_data[section], None)

                        if not isinstance(group_data[section], (MutableMapping, NoneType)):
                            raise AnsibleParserError('Invalid "%s" entry for "%s" group, requires a dictionary, found "%s" instead.' %
                                                     (section, group, type(group_data[section])))

                for key in group_data:

                    if not isinstance(group_data[key], (MutableMapping, NoneType)):
                        self.display.warning('Skipping key (%s) in group (%s) as it is not a mapping, it is a %s' %
                                             (key, group, type(group_data[key])))
                        continue

                    if isinstance(group_data[key], NoneType):
                        self.display.vvv('Skipping empty key (%s) in group (%s)' % (key, group))
                    elif key == 'vars':
                        for var in group_data[key]:
                            self.inventory.set_variable(group, var, group_data[key][var])
                    elif key == 'children':
                        for subgroup in group_data[key]:
                            subgroup = self._parse_group(subgroup, group_data[key][subgroup])
                            self.inventory.add_child(group, subgroup)

                    elif key == 'hosts':
                        for host_pattern in group_data[key]:
                            hosts, port = self._parse_host(host_pattern)
                            self._populate_host_vars(hosts, group_data[key][host_pattern] or {}, group, port)
                    else:
                        self.display.warning(
                            'Skipping unexpected key (%s) in group (%s), only "vars", "children" and "hosts" are valid' % (key, group))

        else:
            self.display.warning("Skipping '%s' as this is not a valid group definition" % group)

        return group

    def _parse_host(self, host_pattern):
        '''
        Each host key can be a pattern, try to process it and add variables as needed
        '''
        (hostnames, port) = self._expand_hostpattern(host_pattern)

        return hostnames, port
