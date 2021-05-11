# Spatium Cepa Platform Collection

![plugin inventory git workflow status](https://github.com/spatium-cepa/ansible-collection-spatiumcepa-platform/actions/workflows/plugin_inventory_git.yml/badge.svg)

This repo contains the `spatiumcepa.platform` Ansible Collection platform engineers and operators.

## Installation

Specify the collection in your ansible requirements a la

```yaml
roles: []

collections:
  - name: git@github.com:spatium-cepa/ansible-collection-spatiumcepa-platform.git
    version: 0.1.2
    type: git
```

Test that collection is available by enabling git inventory plugin, listing docs, then listing empty inventory

```sh
export ANSIBLE_INVENTORY_ENABLED="spatiumcepa.platform.git,ini,host_list,script"

# make sure the git inventory plugin is available
ansible-doc -t inventory -l | grep spatium

# make sure it runs with an empty inventory scan
ansible-inventory -vvv --list
```

Test collection shell output:

```sh
$ ansible-doc -t inventory -l | grep spatium
spatiumcepa.platform.git             Clone and read git repo YAML files as ...

$ ansible-inventory -vvv --list
.....
ansible_collections.spatiumcepa.platform.plugins.inventory.git declined parsing /etc/ansible/hosts as it did not pass its verify_file() method
```

Read abstract inventory example

```sh
ansible-inventory -vvv -i tests/plugins/inventory/git/abstract1 --graph --vars
```

## Usage

### Inventory Example

Read test example1 inventory directory that defines static hosts and loads example1 variable and host definition which includes an inline vaulted variable
And use debug module to list hostvars while limited to the kubernetes_master host group, of which host .8 is only defined in the example1 inventory yaml includes

```sh
cd ~/src/spatium-cepa/ansible-collection-spatiumcepa-platform
pipenv install --python python3.8
pipenv shell

# specify example config and vault-id for vaulted cluster_secret variable
export ANSIBLE_CONFIG=examples/ansible.cfg
export ANSIBLE_VAULT_IDENTITY_LIST="dc1_cluster_secret@tests/plugins/inventory/git/avp_dc1_cluster_secret"

# test collection by installing in local directory
ansible-galaxy collection build --force
rm -rf collections/ansible_collections/spatiumcepa/platform
ansible-galaxy collection install spatiumcepa-platform-0.1.2.tar.gz -p ./collections

# list inventory
ansible-inventory -vvv -i tests/plugins/inventory/git/example1 --list --yaml

# run playbook that will output vaulted cluster_secret variable
ansible-playbook -vvv -i tests/plugins/inventory/git/example1 --limit kubernetes_master playbooks/inventory_git_example1_debug_cluster_secret.yml
```

List inventory output:

```sh
ansible-inventory 2.10.9
  config file = /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/ansible.cfg
  configured module search path = ['/home/nkiraly/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/nkiraly/.local/share/virtualenvs/ansible-collection-spatiumcepa-platform-2rxB0Ia1/lib/python3.8/site-packages/ansible
  executable location = /home/nkiraly/.local/share/virtualenvs/ansible-collection-spatiumcepa-platform-2rxB0Ia1/bin/ansible-inventory
  python version = 3.8.6 (default, Jan 27 2021, 15:42:20) [GCC 10.2.0]
Using /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/ansible.cfg as config file
Parsed /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example1/example1.git.yml inventory source with ansible_collections.spatiumcepa.platform.plugins.inventory.git plugin
ansible_collections.spatiumcepa.platform.plugins.inventory.git declined parsing /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example1/example1_inventory as it did not pass its verify_file() method
Parsed /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example1/example1_inventory inventory source with ini plugin
all:
  children:
    example1:
      children:
        abstract1:
          children:
            db:
              children:
                primary_db:
                  children:
                    db1: {}
                replica_db:
                  children:
                    db2: {}
            web:
              children:
                web1: {}
                web2: {}
        datacenter1:
          children:
            kubernetes:
              children:
                kubernetes_agent:
                  hosts:
                    10.20.1.19:
                      cluster_secret: &id001 !vault |
                        $ANSIBLE_VAULT;1.2;AES256;dc1_cluster_secret
                        36346430333133386364323633343436386537393138376161656361633833343636626136393437
                        3362303061376561666261353836366537626530383132300a383262316636376666623337326237
                        62396132326531653239313861636636306539356361383131323934353931306339393931613530
                        3734633265333131610a643233626431616537306532633163633934626632623831356262386463
                        6664
                      common_var_one: 1
                      common_var_two: 2.0
                      customer_name: nkiraly
                      kubernetes_cluster_node: true
                kubernetes_master:
                  hosts:
                    10.20.1.7:
                      cluster_secret: *id001
                      common_var_one: 1
                      common_var_two: 2.0
                      customer_name: nkiraly
                      kubernetes_cluster_node: true
                      kubernetes_master_node: true
                    10.20.1.8:
                      cluster_secret: *id001
                      common_var_one: 1
                      common_var_two: 2.0
                      customer_name: nkiraly
                      kubernetes_cluster_node: true
                      kubernetes_master_node: true
                      master_10_20_1_8_only_var: tracey
            other_static_host:
              hosts:
                10.50.4.21:
                  common_var_one: 1
                  common_var_two: 2.0
                  customer_name: nkiraly
                  special_var: 135711131719
        kubernetes:
          children:
            kubernetes_agent:
              hosts:
                10.20.1.19: {}
            kubernetes_master:
              hosts:
                10.20.1.7: {}
                10.20.1.8: {}
        kubernetes_master:
          hosts:
            10.20.1.7: {}
            10.20.1.8: {}
    ungrouped: {}
```

Run playbook output:

```sh
ansible-playbook 2.10.9
  config file = /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/ansible.cfg
  configured module search path = ['/home/nkiraly/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/nkiraly/.local/share/virtualenvs/ansible-collection-spatiumcepa-platform-2rxB0Ia1/lib/python3.8/site-packages/ansible
  executable location = /home/nkiraly/.local/share/virtualenvs/ansible-collection-spatiumcepa-platform-2rxB0Ia1/bin/ansible-playbook
  python version = 3.8.6 (default, Jan 27 2021, 15:42:20) [GCC 10.2.0]
Using /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/ansible.cfg as config file
Parsed /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example1/example1.git.yml inventory source with ansible_collections.spatiumcepa.platform.plugins.inventory.git plugin
ansible_collections.spatiumcepa.platform.plugins.inventory.git declined parsing /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example1/example1_inventory as it did not pass its verify_file() method
Parsed /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example1/example1_inventory inventory source with ini plugin
Skipping callback 'default', as we already have a stdout callback.
Skipping callback 'minimal', as we already have a stdout callback.
Skipping callback 'oneline', as we already have a stdout callback.

PLAYBOOK: inventory_git_example1_debug_cluster_secret.yml ************************************************************************************************************************************
1 plays in playbooks/inventory_git_example1_debug_cluster_secret.yml

PLAY [debug cluster secret] ******************************************************************************************************************************************************************
META: ran handlers

TASK [debug cluster secret] ******************************************************************************************************************************************************************
task path: /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/playbooks/inventory_git_example1_debug_cluster_secret.yml:6
ok: [10.20.1.8] => {
    "cluster_secret": "dc0ne"
}
ok: [10.20.1.7] => {
    "cluster_secret": "dc0ne"
}
META: ran handlers
META: ran handlers

PLAY RECAP ***********************************************************************************************************************************************************************************
10.20.1.7                  : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
10.20.1.8                  : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Development

Changes and improvements should be done in a python virtual environment based on the repository Pipfile.

```sh
cd ~/src/spatium-cepa/ansible-collection-spatiumcepa-platform
pipenv install --dev --python python3.8
pipenv shell
```

Then you can build and install the collection locally to run test plays

```sh
# specify example config and vault-id for vaulted cluster_secret variable
export ANSIBLE_CONFIG=examples/ansible.cfg

# test collection by installing in local directory
ansible-galaxy collection build --force
rm -rf collections/ansible_collections/spatiumcepa/platform
ansible-galaxy collection install spatiumcepa-platform-0.1.2.tar.gz -p ./collections

# make sure the git inventory plugin is available
ansible-doc -t inventory -l | grep spatium
# make sure it runs with an empty inventory scan
ansible-inventory -vvv --list
```

```sh
(ansible-collection-spatiumcepa-platform-2rxB0Ia1) nkiraly@galp5-lxw:~/src/spatium-cepa/ansible-collection-spatiumcepa-platform$ ansible-doc -t inventory -l | grep spatium
spatiumcepa.platform.git             Clone and read git repo YAML files as ...

(ansible-collection-spatiumcepa-platform-2rxB0Ia1) nkiraly@galp5-lxw:~/src/spatium-cepa/ansible-collection-spatiumcepa-platform$ ansible-inventory -vvv --list
ansible-inventory 2.10.9
  config file = /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/ansible.cfg
  configured module search path = ['/home/nkiraly/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/nkiraly/.local/share/virtualenvs/ansible-collection-spatiumcepa-platform-2rxB0Ia1/lib/python3.8/site-packages/ansible
  executable location = /home/nkiraly/.local/share/virtualenvs/ansible-collection-spatiumcepa-platform-2rxB0Ia1/bin/ansible-inventory
  python version = 3.8.6 (default, Jan 27 2021, 15:42:20) [GCC 10.2.0]
Using /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/ansible.cfg as config file
Skipping due to inventory source not existing or not being readable by the current user
ansible_collections.spatiumcepa.platform.plugins.inventory.git declined parsing /etc/ansible/hosts as it did not pass its verify_file() method
Skipping due to inventory source not existing or not being readable by the current user
ini declined parsing /etc/ansible/hosts as it did not pass its verify_file() method
[WARNING]: No inventory was parsed, only implicit localhost is available
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}
```

## Testing in playbooks

To streamline development testing, symlink this collection into your playbook virtual environment collections directory, such as:

```sh
cd ~/.local/share/virtualenvs/cloud-platform-management-sy5ngW6F/collections/ansible_collections/spatiumcepa/
ln -s ~/src/spatium-cepa/ansible-collection-spatiumcepa-platform platform
```
