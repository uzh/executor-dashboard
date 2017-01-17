import os

from gc3libs.backends.openstack import OpenStackLrms, OpenStackVMPool

from openstack_dashboard.api.nova import CACERT, INSECURE, nova_client


def inject_nova_client_auth_params(auth_params):
    # Monkey Patching for authentication
    oldOpenstackInit = OpenStackLrms.__init__

    username, token_id, project_id, nova_url, auth_url = auth_params
    c = nova_client.Client('1.1',
                           username,
                           token_id,
                           project_id=project_id,
                           auth_url=auth_url,
                           insecure=INSECURE,
                           cacert=CACERT)
    c.client.auth_token = token_id
    c.client.management_url = nova_url

    def newOpenstackInit(self, *k, **kw):
        oldOpenstackInit(self, *k, **kw)
        self.client = c
        pooldir = os.path.join(os.path.expandvars(OpenStackLrms.RESOURCE_DIR),
                               'vmpool', self.name)
        self._vmpool = OpenStackVMPool(pooldir, self.client)
        print self.client.servers.list()

    OpenStackLrms.__init__ = newOpenstackInit
    # end of monkeypatch
