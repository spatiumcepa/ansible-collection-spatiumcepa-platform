# Spatium Cepa Platform Collection

This repo contains the `spatiumcepa.platform` Ansible Collection which includes modules and plugins for platform operations.

## Usage

Specify the collection in your ansible requirements a la
```yaml
roles: []

collections:
  - name: git@github.com:spatium-cepa/ansible-collection-spatiumcepa-platform.git
    version: 0.1.0
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

Test shell output:

```sh
$ ansible-doc -t inventory -l | grep spatium
spatiumcepa.platform.git             Clone and read git repo YAML files as ...

$ ansible-inventory -vvv --list
.....
ansible_collections.spatiumcepa.platform.plugins.inventory.git declined parsing /etc/ansible/hosts as it did not pass its verify_file() method
```

Read test inventory that loads repository examples

```sh
export ANSIBLE_INVENTORY_ENABLED="spatiumcepa.platform.git,ini,host_list,script"
ansible-inventory -vvv -i tests/plugins/inventory/git --graph --vars
```

Example inventory shell output
```sh
(cloud-platform-management-sy5ngW6F) nkiraly@galp5-lxw:~/src/spatium-cepa/ansible-collection-spatiumcepa-platform$ ansible-inventory -vvv -i tests/plugins/inventory/git --graph --vars
ansible-inventory 2.10.9
  config file = None
  configured module search path = ['/home/nkiraly/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/nkiraly/.local/share/virtualenvs/cloud-platform-management-sy5ngW6F/lib/python3.8/site-packages/ansible
  executable location = /home/nkiraly/.local/share/virtualenvs/cloud-platform-management-sy5ngW6F/bin/ansible-inventory
  python version = 3.8.6 (default, Jan 27 2021, 15:42:20) [GCC 10.2.0]
No config file found; using defaults
Parsed /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example.git.yml inventory source with ansible_collections.spatiumcepa.platform.plugins.inventory.git plugin
ansible_collections.spatiumcepa.platform.plugins.inventory.git declined parsing /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example_inventory as it did not pass its verify_file() method
Parsed /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/example_inventory inventory source with ini plugin
@all:
  |--@include_test:
  |  |--@abstract_test:
  |  |  |--@db:
  |  |  |  |--@primary_db:
  |  |  |  |  |--@db1:
  |  |  |  |--@replica_db:
  |  |  |  |  |--@db2:
  |  |  |  |  |  |--{var005db2 = mo}
  |  |  |  |--{var004db = slo}
  |  |  |--@web:
  |  |  |  |--@web1:
  |  |  |  |  |--{var003web1 = bap}
  |  |  |  |--@web2:
  |  |  |  |--{var002web = bim}
  |  |  |--{var001customer = beep}
  |  |--@example:
  |  |  |--@kubernetes:
  |  |  |  |--@kubernetes_agent:
  |  |  |  |  |--10.20.1.19
  |  |  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |  |  |--{include_var_one = 1}
  |  |  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |  |--@kubernetes_master:
  |  |  |  |  |--10.20.1.7
  |  |  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |  |  |--{include_var_one = 1}
  |  |  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |  |  |  |--{master_node = True}
  |  |  |  |  |--10.20.1.8
  |  |  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |  |  |--{include_var_one = 1}
  |  |  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |  |  |  |--{master_10_20_1_8_only_var = tracey}
  |  |  |  |  |  |--{master_node = True}
  |  |  |  |  |--{master_node = True}
  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |--@other_static_host:
  |  |  |  |--10.50.4.21
  |  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |  |--{include_var_one = 1}
  |  |  |  |  |--{include_var_two = 2.0}
  |  |--@kubernetes:
  |  |  |--@kubernetes_agent:
  |  |  |  |--10.20.1.19
  |  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |  |--{include_var_one = 1}
  |  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |--@kubernetes_master:
  |  |  |  |--10.20.1.7
  |  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |  |--{include_var_one = 1}
  |  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |  |  |--{master_node = True}
  |  |  |  |--10.20.1.8
  |  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |  |--{include_var_one = 1}
  |  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |  |  |--{master_10_20_1_8_only_var = tracey}
  |  |  |  |  |--{master_node = True}
  |  |  |  |--{master_node = True}
  |  |  |--{kubernetes_cluster_node = True}
  |  |--@kubernetes_master:
  |  |  |--10.20.1.7
  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |--{include_var_one = 1}
  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |  |--{master_node = True}
  |  |  |--10.20.1.8
  |  |  |  |--{customer_name = nkiraly}
  |  |  |  |--{include_var_one = 1}
  |  |  |  |--{include_var_two = 2.0}
  |  |  |  |--{kubernetes_cluster_node = True}
  |  |  |  |--{master_10_20_1_8_only_var = tracey}
  |  |  |  |--{master_node = True}
  |  |  |--{master_node = True}
  |  |--{customer_name = nkiraly}
  |  |--{include_var_one = 1}
  |  |--{include_var_two = 2.0}
  |--@ungrouped:
```

## Development

To streamline development testing, symlink this collection into your playbook virtual environment collections directory, such as:

```sh
cd ~/.local/share/virtualenvs/cloud-platform-management-sy5ngW6F/collections/ansible_collections/spatiumcepa/
ln -s ~/src/spatium-cepa/ansible-collection-spatiumcepa-platform platform
```
