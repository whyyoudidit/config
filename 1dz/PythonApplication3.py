import os
import tarfile
import re
import io
import argparse

def cd(cur_dir):
    global path
    global prev
    tarf = tarfile.open(arc)
    res_comm=""
    for j in cur_dir[3::]:
        if (j!=" "):
            res_comm+=j
   
    if (".txt" in res_comm):
        print(f"sh: cd: can't cd to {res_comm}: Not a directory")
        return
            
    if (res_comm[0]=='/'):
        for i in tarf.getnames():
            if (i == res_comm[1::]):
                prev = path
                path = res_comm[1::]
                return
    else:
        if (res_comm=="~"):
            prev = path
            path = ""
            return
        if (res_comm==".."):
            
            if ( path== "" or path.count("/")==0):
                prev = path
                path = ""
                return
        
            else:
                kol = path.count("/")
                flag=0
                i=0
                res=""
                while (flag<kol):
                    if (path[i]=="/"):
                        flag+=1
                        if (flag<kol):
                            
                            res+=path[i]
                            i+=1
                        else:
                            break
                    else:
                        res+=path[i]
                        i+=1
                prev = path
                path= res
                return
        if (res_comm=="-"):
            if (prev!=""):
                print(f"/{prev}")
            else:
                print("/root")
            mem = prev
            prev = path
            path = mem
            return
        pattern = r'(../){2,}|(../)+\.\.'
        if (re.match(pattern, res_comm)):
            for h in range(res_comm.count("..")):
                if ( path== "" or path.count("/")==0):
                    prev = path
                    path = ""
                    if (h==res_comm.count("..")-1):
                        return
        
                else:
                    kol = path.count("/")
                    flag=0
                    i=0
                    res=""
                    while (flag<kol):
                        if (path[i]=="/"):
                            flag+=1
                            if (flag<kol):
                            
                                res+=path[i]
                                i+=1
                            else:
                                break
                        else:
                            res+=path[i]
                            i+=1
                    prev = path
                    path= res
                    if (h==res_comm.count("..")-1):
                        return
                   
        for i in tarf.getnames():
            if (path!=""):
                if (i==path+'/'+res_comm):
                    prev = path
                    path=path+'/'+res_comm
                    return
            else:
                if (i==res_comm):
                    prev = path
                    path=res_comm
                    return
    
    print(f"sh: cd: can't cd to {res_comm}: No such file or directory")

def ls(cur_dir):
    tarf = tarfile.open(arc)
    for i in tarf.getnames():
        
        
        if (os.path.dirname(i) == cur_dir and cur_dir!=""):
            print(i[len(path)+1::], end=" ")
        elif(os.path.dirname(i) == cur_dir):
            print(i, end=" ")
    print("")
def whoami():
    print("vladislav")
def touch(file):
    n=b''
    tarf = tarfile.open(arc, 'a')
    if (' ' not in file):
       
        if ('/' not in file):
            
            if(path!=''):
                for name in tarf.getnames():
                    if (path+"/"+file==name):
                        return
                full_path = f"{path}/{file}"   
            else:
                full_path = file
                for name in tarf.getnames():
                    if (file==name):
                        return
            tarinfo = tarfile.TarInfo(name=full_path)
            tarinfo.size = len(n) 
            tarf.addfile(tarinfo, io.BytesIO(n))
            tarf.close()
            return
        else:
            file = file[1::]
          
            for name in tarf.getnames():
                if (file==name):
                    return
            full_path = file
            tarinfo = tarfile.TarInfo(name=full_path)
            tarinfo.size = len(n) 
            tarf.addfile(tarinfo, io.BytesIO(n))
            tarf.close()
            return
    else:
        files = file.split()
        for i in files:
            for name in tarf.getnames():
                if(path+'/'+i==name):
                    files.remove(i)
  
        for file in files:
            full_path = f"{path}/{file}"   
            tarinfo = tarfile.TarInfo(name=full_path)
            tarinfo.size = len(n) 
            tarf.addfile(tarinfo, io.BytesIO(n))
        tarf.close()
        return

def vshell(cur_dir, listik=[], is_test=0):
    
    global arc
    global path
    global prev
    
    if (len(listik)==0):
        while True:
            if(path==""):
  
                command = input(f"vladislav@localhost:{path}~# ")
            else:
         
                command = input(f"vladislav@localhost:/{path}# ")
            if (command=="ls"):
                ls(path)
            elif(len(command)>=2 and command[0]== "c" and command[1]== "d" ):
                pattern = r'.{2}[ ]*$'
                if (re.fullmatch(pattern, command)):
                    prev = path
                    path = ""
                    continue 
                if(command[2]!=" "):
                    continue
                cd(command)
            elif(command=="exit"):
                break
            elif (command==""):
                continue
            elif (command=="whoami"):
                whoami()
            elif ("touch" in command and len(command)>=7):
                touch(command[6::])
            else:
               print("sh: ",command, ":", " not found", sep="")
    else:
        for i in range(len(listik)):
            command = listik[i]
            if (command=="ls"):
                
                ls(path)
            elif(len(command)>=2 and command[0]== "c" and command[1]== "d" ):
                pattern = r'.{2}[ ]*$'
                if (re.fullmatch(pattern, command)):
                    prev = path
                    path = ""
                    continue
                if(command[2]!=" "):
                    continue
                cd(command)
            elif(command=="exit"):
                break
            elif (command==""):
                continue
            elif (command=="whoami"):
                whoami()
            elif ("touch" in command and len(command)>=7):
                touch(command[6::])
            else:
               print("sh: ",command, ":", " not found", sep="")
        
        if (not(is_test)):
            vshell("")
            
class VM:
    def __init__(self, filesystem_archive: str):
        self.currentpath = ""
        self.filesystem = tarfile.TarFile(filesystem_archive)

    def start(self, arc):
     
      vshell(path)
      
    def run_script(self, script_file: str, is_test):
        
        try:
            with open(script_file, 'r') as file:
                listik=[]
                for line in file:
                    listik.append(line.strip())
                vshell(path, listik, is_test)   
        except FileNotFoundError:
            print(f"Script file '{script_file}' not found.")
    
if __name__ == '__main__':
    path =""
    prev =""
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=str, required=True)
    parser.add_argument('--script', type=str, required=True)
    parser.add_argument('--test', type=bool, required=False)
    args = parser.parse_args()
    arc = args.archive
    vm = VM(args.archive)
    if (args.test):
        vm.run_script(args.script, True)
        
    if args.script:
        
        vm.run_script(args.script, False)
