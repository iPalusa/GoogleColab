import os, sys, time, requests, platform, zipfile, tarfile
from urllib.request import urlretrieve
from subprocess import Popen

HOME = os.path.expanduser("~")
sys.path.append(f"{HOME}/")
if not os.path.exists(f"{HOME}/ocr.py"):
    hCode = "https://raw.githubusercontent.com/biplobsd/" \
                "OneClickRun/master/res/ocr.py"
    urlretrieve(hCode, f"{HOME}/ocr.py")
from ocr import PortForward_wrapper, findPackageR, findProcess, runSh

def tunnel(Server, name):
  os.makedirs(f'{HOME}/content', exist_ok=True)
  if '-nt' in sys.argv:
    with open(f'{HOME}/content/servicesList.csv', 'a') as f:
      f.write(f"{name},{Server.connections[name]['port']},{Server.connections[name]['proto']},{Server.config[1]}\n")
    return ""
  
  mm = False
  tcpmm = Server.connections[name]['proto'] == 'tcp'
  for _ in range(20):
    d = Server.start(name, displayB=False, v=False)
    time.sleep(5)
    #print("<<<<<<<<<<", name, d['url'])
    try:
      if tcpmm: #and (requests.get(d['url']).status_code == 502)
        #print(requests.get(d['url']).status_code)
        mm = True
        break
      elif (not tcpmm) and requests.get(d['url']).ok:  
        mm = True
        break
    except:
       pass
  if not mm:sys.exit(f"[{name.upper()}] tunnel uable url")
  with open(f"{HOME}/content/services.html", "a") as p:
    if tcpmm and Server.SERVICE=='argotunnel':
        p.write(f"{name.upper()} -> cloudflared access tcp --hostname {d['url']} --url localhost:{Server.connections[name]['port']} <br />\n")
    else:    
        p.write(f"{name.upper()} -> <a href='{d['url']}' target='_blank'>{d['url']}</a><br />\n")
  if '-v' in sys.argv:print(d['url'])
  return d['url']

def cusTunnel(config=[]):
  os.makedirs(f'{HOME}/content', exist_ok=True)
  configs = {
    'PORT_FORWARD': 'argotunnel', 
    'protocol': 'tcp',
    'name': 'colab', 
    'port': 8081, 
    'portAcc': 31188, 
    'USE_FREE_TOKEN': True, 
    'TOKEN': "",
    'REGION': "AP"  
  }
  for c in config:
    try:
      n,v = c.split()
      configs[n] = v
    except:
        pass
  #print("-"*55,configs)
  server = PortForward_wrapper(
    configs['PORT_FORWARD'], 
    configs['TOKEN'], 
    eval(str(configs['USE_FREE_TOKEN'])), 
    [[configs['name'], int(configs['port']), configs['protocol']]], 
    configs['REGION'].lower(), 
    [f"{HOME}/.ngrok2/{configs['name']}.yml", int(configs['portAcc'])])
  return tunnel(server, configs['name'])

def ghfs():
    USE_FREE_TOKEN = True  # @param {type:"boolean"}
    TOKEN = ""  # @param {type:"string"}
    REGION = "AP" #@param ["US", "EU", "AP", "AU", "SA", "JP", "IN"]
    OUTPUT_DIR = "/"  # @param {type:"string"}
    PORT_FORWARD = "ngrok" #@param ["ngrok", "localhost", "argotunnel"]
    #HOME = f'{HOME}/content'
    toolLocation = f'{HOME}/tools/ghfs'
    binaryF = f"{toolLocation}/ghfs"

    os.makedirs(toolLocation, exist_ok=True)

    if not os.path.exists(binaryF):
      DZipBL = f"{toolLocation}/Zipghfs.zip"
      urlretrieve(
          findPackageR("mjpclab/go-http-file-server", "linux-amd64.zip"), DZipBL)
      with zipfile.ZipFile(DZipBL, 'r') as zip_ref:zip_ref.extractall(toolLocation)
      os.remove(DZipBL)
      os.chmod(binaryF, 0o777)

    if not findProcess("ghfs", "--listen-plain"):
      runSh(f'./ghfs --listen-plain 1717 -R \
             -a ":/:{OUTPUT_DIR}" \
             --global-upload \
             --global-mkdir \
             --global-delete \
             --global-archive \
             --global-archive \
              &', 
            shell=True,
            cd=f"{HOME}/tools/ghfs")

    # START_SERVER
    # Ngrok region 'us','eu','ap','au','sa','jp','in'
    server = PortForward_wrapper(
        PORT_FORWARD, TOKEN, USE_FREE_TOKEN, [['ghfs', 1717, 'http']], REGION.lower(), 
        [f"{HOME}/.ngrok2/ghfs.yml", 4171]
    )
    return tunnel(server, 'ghfs')

def wetty(port=4343):
  USE_FREE_TOKEN = True  # @param {type:"boolean"}
  TOKEN = ""  # @param {type:"string"}
  REGION = "AP" #@param ["US", "EU", "AP", "AU", "SA", "JP", "IN"]
  OUTPUT_DIR = "/"  # @param {type:"string"}
  PORT_FORWARD = "ngrok"
  HOME = '/content'
  os.makedirs(f'{HOME}/tools/temp', exist_ok=True)
  wettyBF = 'https://github.com/biplobsd/temp/releases/download/v0.001/wetty.tar.gz'
  fileSN = f'{HOME}/tools/temp/wetty.tar.gz'
  urlretrieve(wettyBF, fileSN)
  with tarfile.open(fileSN, 'r:gz') as t:t.extractall(f'{HOME}/tools/')
  os.remove(fileSN)
  Popen(
      f'{HOME}/tools/wetty/wetty --port {port} --bypasshelmet -b "/" -c "/bin/bash"'.split(),
      cwd=os.getcwd())
  server = PortForward_wrapper(
    PORT_FORWARD, TOKEN, USE_FREE_TOKEN, [['wetty', '4343', 'http']], 
    REGION.lower(), 
    [f"{HOME}/.ngrok2/wetty.yml", 31199])
  return tunnel(server, 'wetty')


if platform.system() == "Linux":
  if 'ghfs' in sys.argv:
    name = "Installing go-http-file-server ..."
    print(name)
    ghfs()
  
  if 'wetty' in sys.argv:
    name = "Installing wetty ..."
    print(name)
    wetty()

  if '-cpf' in sys.argv:
    print("...><..."*50)
    cusTunnel(sys.argv)
