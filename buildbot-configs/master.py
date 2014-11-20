# -*- python -*-
# ex: set syntax=python:

# This is a sample buildmaster config file. It must be installed as
# 'master.cfg' in your buildmaster's base directory.

# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
c = BuildmasterConfig = {}

####### BUILDSLAVES

# The 'slaves' list defines the set of recognized buildslaves. Each element is
# a BuildSlave object, specifying a unique slave name and password.  The same
# slave name and password must be configured on the slave.
from buildbot.buildslave import BuildSlave
c['slaves'] = [BuildSlave("myslave", "111")]

# 'protocols' contains information about protocols which master will use for
# communicating with slaves.
# You must define at least 'port' option that slaves could connect to your master
# with this protocol.
# 'port' must match the value configured into the buildslaves (with their
# --master option)
c['protocols'] = {'pb': {'port': 9989}}

####### CHANGESOURCES

# the 'change_source' setting tells the buildmaster how it should find out
# about source code changes.  Here we point to the buildbot clone of pyflakes.

from buildbot.changes.gitpoller import GitPoller
c['change_source'] = []
#c['change_source'].append(GitPoller(
#        'git://github.com/MirantisLabs/pumphouse.git',
#        workdir='gitpoller-workdir', branch='master',
#        pollinterval=300))

####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.  In this
# case, just kick off a 'runtests' build

from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.basic import Dependent
from buildbot.changes import filter
c['schedulers'] = []
#c['schedulers'].append(SingleBranchScheduler(
#                            name="all",
#                            change_filter=filter.ChangeFilter(branch='master'),
#                            treeStableTimer=None,
#                            builderNames=["runtests"]))

deploy_chairs = ForceScheduler(
    name="superforce",
    builderNames=["deploy_devstack1", "deploy_devstack2"])

c['schedulers'].append(deploy_chairs)

deploy_component = Dependent(
    name="superpump",
    upstream=deploy_chairs,
    builderNames=["deploy_pumphouse"])

c['schedulers'].append(deploy_component)

####### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which slaves can execute them.  Note that any particular build will
# only take place on one slave.

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand

openstack_user = "USER"
openstack_password = "PASS"
openstack_tenant = "TENANT"
keystone_url = "http://localhost:5000"
image_id = "IMAGE_ID"
flavor_id = "FLAVOR_ID"
net_id = "NET_ID"
keypair = "KEYPAIR"
pump_flavor_id = "FLAVOR_ID"

devstack1 = BuildFactory()

devstack1.addStep(Git(repourl='git://github.com/smurashov/test-infra.git',
                      mode='full'))

devstack1.addStep(
    ShellCommand(
        command=["bash", "-c",
                 "expect deploy-devstack.sh ubuntu "
                 "`python create_vm.py -openstack_user %s "
                 "-openstack_password %s "
                 "-openstack_tenant %s "
                 "-keystone_url %s "
                 "-server_name cidevstack1 "
                 "-image_id %s "
                 "-flavor_id %s "
                 "-net_id %s "
                 "-keypair %s`" %
                 (openstack_user, openstack_password,
                  openstack_tenant, keystone_url, image_id, flavor_id,
                 net_id, keypair)]))

devstack2 = BuildFactory()

devstack2.addStep(Git(repourl='git://github.com/smurashov/test-infra.git',
                      mode='full'))

devstack2.addStep(
    ShellCommand(
        command=["bash", "-c",
                 "expect deploy-devstack.sh ubuntu "
                 "`python create_vm.py -openstack_user %s "
                 "-openstack_password %s "
                 "-openstack_tenant %s "
                 "-keystone_url %s "
                 "-server_name cidevstack2 "
                 "-image_id %s "
                 "-flavor_id %s "
                 "-net_id %s "
                 "-keypair %s`" %
                 (openstack_user, openstack_password,
                  openstack_tenant, keystone_url, image_id, flavor_id,
                 net_id, keypair)]))

pumphouse = BuildFactory()

pumphouse.addStep(Git(repourl='git://github.com/smurashov/test-infra.git',
                      mode='full'))

pumphouse.addStep(ShellCommand(command=["rm", "-f", "result.yaml"]))

pumphouse.addStep(
    ShellCommand(
        command=["bash", "-c",
                 "python pump-conf/config-generator.py "
                 "-source_ip `nova --os-username {0} "
                 "--os-tenant-name {1} "
                 "--os-auth-url {2} "
                 "--os-password {3} list | "
                 "grep cidevstack1 | "
                 "tr '|' '\n' | grep ci_network | tr '=' '\n' | tail -1` "
                 "-destination_ip `nova --os-username {0} "
                 "--os-tenant-name {1} "
                 "--os-auth-url {2} "
                 "--os-password {3} list | "
                 "grep cidevstack2 | "
                 "tr '|' '\n' | grep ci_network "
                 "| tr '=' '\n' | tail -1`".format(
                     openstack_user, openstack_tenant, keystone_url,
                     openstack_password
                 )]
    ))

pumphouse.addStep(
    ShellCommand(
        command=["bash", "-c",
                 "expect deploy-pump.sh ubuntu "
                 "`python create_vm.py -openstack_user %s "
                 "-openstack_password %s "
                 "-openstack_tenant %s "
                 "-keystone_url %s "
                 "-server_name cipumphouse "
                 "-image_id %s "
                 "-flavor_id %s "
                 "-net_id %s "
                 "-keypair %s`" %
                 (openstack_user, openstack_password,
                  openstack_tenant, keystone_url, image_id, pump_flavor_id,
                 net_id, keypair)]))

from buildbot.config import BuilderConfig

c['builders'] = []
c['builders'].append(
    BuilderConfig(name="deploy_devstack1",
      slavenames=["myslave"],
      factory=devstack1))
c['builders'].append(   
    BuilderConfig(name="deploy_devstack2",
      slavenames=["myslave"],
      factory=devstack2))
c['builders'].append(
    BuilderConfig(name="deploy_pumphouse",
      slavenames=["myslave"],
      factory=pumphouse))

####### STATUS TARGETS

# 'status' is a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

c['status'] = []

from buildbot.status import html
from buildbot.status.web import authz, auth

authz_cfg=authz.Authz(
    # change any of these to True to enable; see the manual for more
    # options
    auth=auth.BasicAuth([("superman","swordfish")]),
    gracefulShutdown=False,
    forceBuild=auth,  # use this to test your slave once it is set up
    forceAllBuilds=auth,
    pingBuilder=False,
    stopBuild=False,
    stopAllBuilds=False,
    cancelPendingBuild=False,
)
c['status'].append(html.WebStatus(http_port=8010, authz=authz_cfg))

####### PROJECT IDENTITY

# the 'title' string will appear at the top of this buildbot
# installation's html.WebStatus home page (linked to the
# 'titleURL') and is embedded in the title of the waterfall HTML page.

c['title'] = "MyBlackJack"
c['titleURL'] = "https://github.com/MirantisLabs/pumphouse"

# the 'buildbotURL' string should point to the location where the buildbot's
# internal web server (usually the html.WebStatus page) is visible. This
# typically uses the port number set in the Waterfall 'status' entry, but
# with an externally-visible host name which the buildbot cannot figure out
# without some help.

c['buildbotURL'] = "http://localhost:8010/"

####### DB URL

c['db'] = {
    # This specifies what database buildbot uses to store its state.  You can leave
    # this at its default for all but the largest installations.
    'db_url' : "sqlite:///state.sqlite",
}

