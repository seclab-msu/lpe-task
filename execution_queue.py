import psycopg2
import time
import subprocess
import tempfile
import  sys
IP = sys.argv[1]
PASSWORD = sys.argv[2]

def execute_file(exe):
    try:
        # Just to be sure
        print(subprocess.check_output('VBoxManage controlvm "LPE-TASK" poweroff 2>&1 || true', shell=True).decode('utf-8'))
        print(subprocess.check_output('VBoxManage snapshot "LPE-TASK" restore "INITIAL" 2>&1 || true' , shell=True).decode('utf-8'))
        print(subprocess.check_output('VBoxManage startvm "LPE-TASK"  --type headless 2>&1', shell=True).decode('utf-8'))
        time.sleep(60*5) # give 5 minutes to start
        print("Starting evil-winrm")
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(exe)
            temp.flush()
            cmd="""
            bash -c "(echo 'upload %s C:\Windows\Temp\exploit.exe' ; echo 'C:\Windows\Temp\exploit.exe'; echo exit )  | evil-winrm -i %s -u user -p '%s' -n 2>&1"
            """ % (temp.name, IP, PASSWORD)
            out = subprocess.check_output(cmd, shell=True, timeout=60*5).decode('utf-8')
            return "DONE", out
    except subprocess.CalledProcessError as e:
        return "FAIL", "cmd %s returncode %d out %s err %s. If you see errors related to VBoxManage and retrying does not help, contact @webpentest in tg" % (e.cmd, e.returncode, e.stdout, e.stderr)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", ""
    finally:
        try:
            print(subprocess.check_output('VBoxManage controlvm "LPE-TASK" poweroff 2>&1', shell=True).decode('utf-8'))
            print(subprocess.check_output('VBoxManage snapshot "LPE-TASK" restore "INITIAL" 2>&1', shell=True).decode('utf-8'))
        except subprocess.CalledProcessError as e:
            pass
while True:
    try:
        conn = psycopg2.connect(dbname='hello_flask_dev', user='hello_flask', password='hello_flask', host='localhost', port='15432')
        cur = conn.cursor()
        cur.execute("select count(*) from submission where status = 'NEW';")
        count = cur.fetchone()[0]
        if count > 0:
            cur.execute("select id, uuid, name, exe from submission where status = 'NEW' order by id asc limit 1;")
            file_id, uuid, name, exe = cur.fetchone()
            print('Processing file: id %d uuid %s name %s length %d' %(file_id, uuid, name, len(exe)))
            cur.execute('BEGIN')
            cur.execute("update submission set status=%s where id=%s", ("IN_PROGRESS", file_id))
            cur.execute('COMMIT')
            status, output = execute_file(exe)
            print('Result: status %s output %s' % (status, output))
            cur.execute('BEGIN')
            cur.execute("update submission set status=%s, output=%s where id=%s", (status, output, file_id))
            cur.execute('COMMIT')
        else:
            time.sleep(1)
    except KeyboardInterrupt:
        break
