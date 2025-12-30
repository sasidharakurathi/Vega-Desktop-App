import GPUtil

gpus = GPUtil.getGPUs()
if gpus:
    gpu = gpus[0]
    print(f"GPU ID: {gpu.id}, Name: {gpu.name}")
    print(f"Load: {gpu.load * 100:.2f}%")
    print(f"Memory Free: {gpu.memoryFree}MB")
    print(f"Memory Used: {gpu.memoryUsed}MB")
    print(f"Memory Total: {gpu.memoryTotal}MB")
    print(f"Temperature: {gpu.temperature} °C")