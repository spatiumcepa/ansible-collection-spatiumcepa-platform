from ansible.plugins.inventory import BaseInventoryPlugin


class InventoryModule(BaseInventoryPlugin):  # TODO: implement Cacheable

    NAME = 'spatiumcepa.platform.git'

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('git.yaml', 'git.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        config = self._read_config_data(path)

        # if NOT using _read_config_data you should call set_options directly,
        # to process any defined configuration for this plugin,
        # if you don't define any options you can skip
        # self.set_options()

        # example consuming options from inventory source
        mysession = bzorpazorplib.session(user=self.get_option('api_user'),
                                          password=self.get_option('api_pass'),
                                          server=self.get_option('api_server')
                                          )

        # make requests to get data to feed into inventory
        mydata = mysession.getitall()

        # raise AnsibleParserError if source cannot be read or there is an error in doing so

        # parse data and create inventory objects:
        for colo in mydata:
            for server in mydata[colo]['servers']:
                self.inventory.add_host(server['name'])
                self.inventory.set_variable(server['name'], 'ansible_host', server['external_ip'])
