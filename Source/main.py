# main.py
from Controllers.command_parser import CommandParser

def main():
    print("Matching Engine started. Type 'exit' or 'quit' to stop.")
    
    command_parser = CommandParser()

    while True:
        try:
            comando = input(">>> ").strip()
            
            if comando.lower() in ['exit', 'quit']:
                break
                
            if not comando:
                continue
            command_parser.process(comando)
            
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()