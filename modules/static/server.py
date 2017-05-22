import sys
import time
import os
sys.path.append('./gen-py')
from staticAnalyzer import StaticAnalyze
from staticAnalyzer.ttypes import *
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import time
from utils import Transfer
import glob


class analyzerHandler:

    def connect(self):
        return "Connected"
    def analyze(self, bin_path, report_dir):

        root_dir = os.path.abspath(".")
        sep = os.path.sep
        local_bin_path = root_dir + sep + "temp" + sep + "temp.macho"
        local_report = root_dir + sep + 'report'
        xmls = glob.glob(local_report + sep + '*.xml')
        for xml in xmls:
            os.remove(xml)
        Transfer().sftp_get(bin_path, local_bin_path)
        time.sleep(10)
        os.chdir(os.path.abspath('.') + os.path.sep + 'lib')
        cmd = 'java -jar ios-vulnerability-detection_fat.jar ' + local_bin_path + " " + local_report
        print cmd
        os.popen(cmd)
        # subprocess.call(cmd, shell=True)
        os.chdir(os.path.abspath('..'))
        print 'static analyse success!'
        report_xml = glob.glob(local_report + sep + '*.xml')[0]
        file_name = report_xml.split(sep).pop()
        Transfer().sftp_put(report_dir + '/' + file_name, report_xml)
        return report_dir + '/' + file_name

handler = analyzerHandler()
processor = StaticAnalyze.Processor(handler)
transport = TSocket.TServerSocket("192.168.2.74", 9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
print "Starting thrift server in python..."
# analyzerHandler().analyze("bin_path", "rep_path")
server.serve()
print "done!"