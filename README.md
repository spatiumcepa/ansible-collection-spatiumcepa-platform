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

Read abstract inventory example

```sh
ansible-inventory -vvv -i tests/plugins/inventory/git/abstract1 --graph --vars
```

Read test example1 inventory directory that defines static hosts and loads example1 variable and host definition which includes an inline vaulted variable
And use debug module to list hostvars while limited to the kubernetes_master host group, of which host .8 is only defined in the example1 inventory yaml includes

```sh
# specify vault-id for vaulted cluster_secret variable
export ANSIBLE_CONFIG=tests/plugins/inventory/git/ansible.cfg
export ANSIBLE_VAULT_IDENTITY_LIST="dc1_cluster_secret@tests/plugins/inventory/git/avp_dc1_cluster_secret"

# list inventory
ansible-inventory -vvv -i tests/plugins/inventory/git/example1 --list --yaml

# run playbook that will output vaulted cluster_secret variable
ansible-playbook -vvv -i tests/plugins/inventory/git/example1 --limit kubernetes_master tests/plugins/inventory/git/debug_cluster_secret.yml
```

List inventory output:

```sh
ansible-inventory 2.10.9
  config file = /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/ansible.cfg
  configured module search path = ['/home/nkiraly/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/nkiraly/.local/share/virtualenvs/cloud-platform-management-sy5ngW6F/lib/python3.8/site-packages/ansible
  executable location = /home/nkiraly/.local/share/virtualenvs/cloud-platform-management-sy5ngW6F/bin/ansible-inventory
  python version = 3.8.6 (default, Jan 27 2021, 15:42:20) [GCC 10.2.0]
Using /home/nkiraly/src/spatium-cepa/ansible-collection-spatiumcepa-platform/tests/plugins/inventory/git/ansible.cfg as config file
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
                        32646364343663633161623932326438336231393264396531333539666464353862323130353932
                        3030313762356432376331616337623531623266313734320a613230366130366562646264303938
                        33656536656132313032353630663339323133306562396366306131376162626231633230633335
                        6539663834636366650a323065366230653231376134323138356430376235313761636338663931
                        3539
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

## Development

To streamline development testing, symlink this collection into your playbook virtual environment collections directory, such as:

```sh
cd ~/.local/share/virtualenvs/cloud-platform-management-sy5ngW6F/collections/ansible_collections/spatiumcepa/
ln -s ~/src/spatium-cepa/ansible-collection-spatiumcepa-platform platform
```
