import psutil

for proc in psutil.process_iter():
    try:
        # this returns the list of opened files by the current process
        flist = proc.open_files()
        if flist:
            print(proc.pid,proc.name)
            for nt in flist:
                print("\t",nt.path)

    # This catches a race condition where a process ends
    # before we can examine its files    
    except psutil.NoSuchProcess as err:
        print("****",err) 