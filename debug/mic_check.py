import speech_recognition as sr

def list_microphones():
    mics = sr.Microphone.list_microphone_names()
    print("\n------------------------------------------------")
    print(" AVAILABLE AUDIO DEVICES")
    print("------------------------------------------------")
    for index, name in enumerate(mics):
        print(f"ID: {index}  |  Name: {name}")
    print("------------------------------------------------\n")

if __name__ == "__main__":
    list_microphones()