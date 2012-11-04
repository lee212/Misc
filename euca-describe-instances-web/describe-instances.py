import cherrypy
import subprocess
import sys
import re
import Xml2Dict

class DescribeInstances:

    rawoutput = None
    xmloutput = None
    xml2dict = None
    platform = None

    def list_instances(self):
        res1 = self.list_eucalyptus()
        res2 = self.list_openstack()
        res = res1 + res2
        
        return res

    def list_eucalyptus(self):
        self.platform = "eucalyptus"
        self.read_from_cmd([ "euca-describe-instances", "verbose", "--config", "/home/hyungro/.futuregrid/eucalyptus/admin/eucarc", "--debug"])
        self.convert_to_dict_from_xml()
        return self.display()

    def list_openstack(self):
        return ""
        self.platform = "openstack"
        self.read_from_cmd([ "euca-describe-instances", "verbose", "--config", "/home/hyungro/.futuregrid/openstack/novarc", "--debug"])
        self.convert_to_dict_from_xml()
        return self.display()

    def display(self):
        #for i in self.xml2dict.iteritems():
        #    print i
        res = "<h1>"+self.platform.title()+"</h1>"
        res = res + "<table border=1>"+self.print_ins(self.xml2dict)+"</table>"
#        print res
        return res

    def read_from_cmd(self, cmd):
        run_euca_describe_instances = cmd
        self.rawoutput = subprocess.check_output(run_euca_describe_instances, stderr=subprocess.STDOUT).splitlines()

        for line in self.rawoutput:
            if re.search("DescribeInstancesResponse", line):
                self.xmloutput = line.split("[DEBUG]:")[1]
                break

    def convert_to_dict_from_xml(self):
        xml2dict = Xml2Dict.Xml2Dict(self.xmloutput)
        self.xml2dict = xml2dict.parse()

    def convert_to_dict_from_stdout(self):

        # http://docs.amazonwebservices.com/AWSEC2/latest/CommandLineReference/ApiReference-cmd-DescribeInstances.html
        #
        # example:
        #
        # RESERVATION   r-078141E6  110223663177    default
        # INSTANCE    i-DA574028  emi-A8F63C29    149.165.158.203 10.131.178.57   running selvikey    0       m1.small    2012-10-17T23:58:18.188Z    euca3india  eki-226638E6    eri-32DE3771        monitoring-disabled 149.165.158.203 10.131.178.57           instance-store                                  
        # RESERVATION r-982D3FA6  458299102773    default
        # INSTANCE    i-44014279  emi-FB4A3E74    149.165.158.223 10.133.83.96    running     0       m1.small    2012-09-17T19:23:37.693Z    euca3india  eki-226638E6    eri-32DE3771        monitoring-disabled 149.165.158.223 10.133.83.96            instance-store                                  
        # RESERVATION r-3DAE42F2  159083787446    default
        # INSTANCE    i-80924259  emi-805D3DBD    149.165.158.228 10.150.212.78   running my-instance1    0       m1.large    2012-09-23T20:53:19.016Z    euca3india  eki-226638E6    eri-32DE3771        monitoring-disabled 149.165.158.228 10.150.212.78           instance-store                                  
        #
        # RESERVATION     r-705d5818      111122223333    default
        # INSTANCE        i-53cb5b38      ami-b232d0db    ec2-184-73-10-99.compute-1.amazonaws.com domU-12-31-39-00-A5-11.compute-1.internal        running         0               m1.small 2010-04-07T12:49:28+0000 us-east-1a      aki-94c527fd    ari-96c527ff            monitoring-disabled       184.73.10.99    10.254.170.223                  ebs   paravirtual  xen
        # BLOCKDEVICE     /dev/sda1       vol-a36bc4ca    2010-04-07T12:28:01.000Z
        # BLOCKDEVICE     /dev/sdb        vol-a16bc4c8    2010-04-07T12:28:01.000Z
        # RESERVATION     r-705d5818      111122223333    default
        # INSTANCE        i-39c85852      ami-b232d0db    terminated      gsg-keypair       0               m1.small        2010-04-07T12:21:21+0000        us-east-1a      aki-94c527fd      ari-96c527ff            monitoring-disabled                              ebs   paravirtual  xen
        # RESERVATION     r-9284a1fa      111122223333    default
        # INSTANCE        i-996fc0f2      ami-3c47a355    ec2-184-73-195-182.compute-1.amazonaws.com domU-12-31-39-09-25-62.compute-1.internal       running keypair    0               m1.small  2010-03-17T13:17:41+0000        us-east-1a      aki-a71cf9ce    ari-a51cf9cc     monitoring-disabled      184.73.195.182  10.210.42.144                   instance-store   paravirtual  xen
        #########################
        # The RESERVATION identifier
        # The ID of the reservation
        # The AWS account ID
        # The name of each security group the instance is in (for instances not running in a VPC)
        #########################
        # The INSTANCE identifier
        # The ID of each running instance
        # The AMI ID of the image on which the instance is based
        # The public DNS name associated with the instance. This is only present for instances in the running state.
        # The private DNS name associated with the instance. This is only present for instances in the running state.
        # The state of the instance
        # The key name. If a key was associated with the instance at launch, its name will appear.
        # The AMI launch index
        # The product codes associated with the instance
        # The instance type

        # The instance launch time
        # The Availability Zone
        # The ID of the kernel
        # The ID of the RAM disk
        # The monitoring state
        # The public IP address

        # The private IP addresses associated with the instance. Multiple private IP addresses are only available in Amazon VPC.
        # The tenancy of the instance (if the instance is running within a VPC). An instance with a tenancy of dedicated runs on single-tenant hardware.
        # The subnet ID (if the instance is running in a VPC)
        # The VPC ID (if the instance is running in a VPC)
        # The type of root device (ebs or instance-store)
        # The placement group the cluster instance is in
        # The virtualization type (paravirtual or hvm)
        # The ID of each security group the instance is in (for instances running in a VPC)
        # Any tags assigned to the instance
        # The hypervisor type (xen or ovm)
        #########################
        # The BLOCKDEVICE identifier (one for each Amazon EBS volume, if the instance has a block device mapping), along with the device name, volume ID, and timestamp
        lines = self.output.split("\n")

        prog = re.compile( r'(?P<rsv_title>\w+)\s+(?P<rsv_id>[\w-]+)\s+(?P<account_id>\w+)\s+(?P<security_group>\w+)\n\
                (?P<ins_title>\w+)\s+(?P<ins_id>[\w-]+)\s+(?P<ami_id>[\w-]+)\s+(?P<public_dns>[\d.]+)\s+(?P<state>\w+)\s+(?P<owner_id>[\w-]+)\s+(?P<launch_index>\d+)\s+(?P<ins_type>[\w.]+)\s+\
                (?P<ins_launch_time>[\dT:+-Z]+)\s+(?P<availability_zone>[\w-]+)\s+(?P<kernel_id>[\w-]+)\s+(?P<ramdisk_id>[\w-]+)\s+(?P<monitoring_state>[\w-]+)\s+(?P<public_ip>[\d.]+)\s+\
                (?P<private_ip>[\d.]+)\s+(?P<tenancy>[\w-]+)\s+(?P<vir_type>\w+)\s+(?P<hyper_type>\w+)', re.M|re.I)

    def print_ins(self, dictionary, ident = '', braces=1):
        all_msg = ""
        for key, value in dictionary.iteritems():
            msg = ""
            if isinstance(value, dict):
                #msg = '%s%s%s%s' %(ident,braces*'[',key,braces*']') 
                if braces == 2:
                    msg = "<tr>"
                msg = msg + self.print_ins(value, ident+'  ', braces+1)
            else:
                msg = '%s' %(value)
                msg = "<td>" + msg + "</td>"
            all_msg = all_msg + msg

        return all_msg

    def print_dict(self, dictionary, ident = '', braces=1):
        """ Recursively prints nested dictionaries."""

        for key, value in dictionary.iteritems():
            if isinstance(value, dict):
                print '%s%s%s%s' %(ident,braces*'[',key,braces*']') 
                self.print_dict(value, ident+'  ', braces+1)
            else:
                print ident+'%s = %s' %(key, value)

    def output(self):
        return "Hello World!"

class DescribeInstancesWeb(object):

    def __init__(self):
        self.ins = DescribeInstances()

    def index(self):
        return self.ins.output()

    def list(self):
        return self.ins.list_instances()

    index.exposed = True
    list.exposed = True

if len(sys.argv) > 1 and sys.argv[1] == "cmd":
    obj = DescribeInstances()
    obj.list_instances()
else:
    cherrypy.config.update({'server.socket_host': '129.79.49.179',
        'server.socket_port': 8080,
        })
    cherrypy.quickstart(DescribeInstancesWeb())
