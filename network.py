import telnetlib
import time
import sys
import os
import re
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import email
import email.mime.application
input_cmd = ["sh clock", "sh cpu", "sh memory", "sh vpn-sessiondb summary", "sh cpu detailed", "sh asp drop", "sh conn", "sh crashinfo"]
pager_size = ["conf t", "pager 2147483647", "end"]
attachfile = '{}.txt'.format(sys.argv[5])
output = ""
output_list = []
cwd = os.getcwd()
host = sys.argv[1]
tn=telnetlib.Telnet(host)
tn.read_until(b"Username:", 2)
tn.write(b"{}\n".format(sys.argv[2]))
tn.read_until(b"Password:", 2)
tn.write(b"{}\n".format(sys.argv[3]))
tn.read_until(b">", 2)
tn.write(b"en\n")
tn.read_until(b"Password:", 2)
tn.write(b"{}\n".format(sys.argv[4]))
tn.read_until(b"#", 2)
for i in pager_size:
    tn.write(b"{}\n".format(i))
    tn.read_until(b"#", 2)
    time.sleep(2)

for i in input_cmd:
    tn.write(b"{}\n".format(i))
    result = tn.read_until(b"#", 50)
    output = output + result
    output = output + "\n================================================================================================================================\n"
    output_list.append(result)
    time.sleep(3)
tn.close

 

###########################################################################################

cpu_util = re.search(r'CPU utilization for 5 seconds = (.*); 1 minute: (.*); 5 minutes: (.*)\n', str(output_list[1]))

mem_used = re.search(r'Used memory(.*)bytes \((.*)\)',str(output_list[2]))

mem_total = re.search(r'Total memory(.*)bytes \((.*)\)',str(output_list[2]))

 

###########################################################################################

table=['<html><body><table border="1">']

table.append(r'<tr><td style="background-color:mediumorchid; font-weight:bold" font="bold" align="center">CPU Last 5 Sec</td><td style="background-color:mediumorchid; font-weight:bold" font="bold" align="center">CPU Last 1 Min</td><td style="background-color:mediumorchid; font-weight:bold" font="bold" align="center">CPU Last 5 Min</td></tr>')

table.append(r'<tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td>' % (cpu_util.group(1),cpu_util.group(2),cpu_util.group(3)))

table.append('</table></body></html>')

table_cpu_util = ''.join(table)

 

table_mem=['<html><body><table border="1">']

table_mem.append(r'<tr><td style="background-color:mediumorchid; font-weight:bold" font="bold" align="center">Used Memory</td><td style="background-color:mediumorchid; font-weight:bold" font="bold" align="center">Total Memory</td></tr>')

table_mem.append(r'<tr><td align="center">%s</td><td align="center">%s</td></tr>'% (mem_used.group(2),mem_total.group(2)))

table_mem.append('</table></body></html>')

table_mem_usage = ''.join(table_mem)

###########################################################################################

out = "%s\%s"%(cwd,attachfile)

out_file = open(out, "w")

out_file.write(output)

time.sleep(5)

out_file.close()

 

sender = 'gopselva@cisco.com'

receivers = '%s' % (sys.argv[6])

smtpaddr = 'xch-rtp-007.cisco.com'

 

subject = "ST : Monitoring Status for the Device : %s" %sys.argv[1]

body = ("""Hi Team,

<br></br>

<br>Time :</br>

<br>%s</br>

<br>CPU Utilization Details :</br>

<br>%s</br>

<br>Memory Usage Details :</br>

<br>%s</br>

<br>Thanks & Regards,</br>System Test Team"""%(output_list[0], table_cpu_util, table_mem_usage))

msg = MIMEMultipart()

msg = MIMEMultipart('alternative')

msg['Subject'] = subject

msg['From'] = sender

msg['To'] = receivers

html_body = MIMEText(body, 'html')

attachment = MIMEBase('application', "octet-stream")

attachment.set_payload(open("%s/%s"% (cwd,attachfile), "rb").read())

encoders.encode_base64(attachment)

attachment.add_header('Content-Disposition', 'attachment; filename=%s' % attachfile)

   

msg.attach(html_body)

msg.attach(attachment)

 

try:

    smtpObj = smtplib.SMTP('%s' % smtpaddr)

    smtpObj.sendmail(msg['From'], msg["To"].split(","), msg.as_string())

    print "Successfully sent email"

except SMTPException:

    print "Error: unable to send email"
