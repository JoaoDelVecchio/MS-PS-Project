import time
import sys
import os
import io

# Garante que o Python encontre a raiz da pasta 'Source' para fazer os imports corretamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Controllers.command_parser import CommandParser

def suppress_stdout():
    return io.StringIO()

def run_benchmarks():
    print("===============================================================")
    print(" Testes de Tempo de Execução - MATCHING ENGINE ")
    print("===============================================================")

    parser = CommandParser()

    N_ORDERS = 10_000
    N_LEVELS = 100

    print(f"[{time.strftime('%H:%M:%S')}] Fase 1: População do LOB...")
    print(f" Inserindo {N_ORDERS:,} ordens distribuídas em {N_LEVELS} níveis de preço...")

    old_stdout = sys.stdout
    sys.stdout = suppress_stdout()

    start_setup = time.perf_counter()
    
    # Bids vão de 1 a 100 | Asks vão de 110 a 209 (Garante um Spread vazio entre 100 e 110)
    for i in range(1, N_ORDERS + 1):
        side = "buy" if i <= N_ORDERS // 2 else "sell"
        if side == "buy":
            price = (i % N_LEVELS) + 1
        else:
            price = (i % N_LEVELS) + 110
        
        # Como qty é 10, cada nível terá 50 ordens, totalizando 500 de volume por nível
        parser.process(f"limit {side} {price} 10")
        
    end_setup = time.perf_counter()
    
    sys.stdout = old_stdout
    print(f" LOB populado com sucesso em {(end_setup - start_setup):.2f} segundos.")
    print("---------------------------------------------------------------")
    print(f"Medições com o Livro com {N_ORDERS:,} de Ordens ativas:")
    print()

    # Teste de Inserção (Cai numa Fila Encadeada que já existe)
    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process("limit buy 50 100")
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Inserir Ordem Limite (Nível Existente) O(1) : {(end_t - start_t) * 1_000_000:.2f} microssegundos")

    # Teste de Inserção (Cria um novo Nível de Preço no Array/Dict)
    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process("limit buy 50.5 100")
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Inserir Ordem Limite (Novo Nível de Preço)  : {(end_t - start_t) * 1_000_000:.2f} microssegundos")

    target_id = f"id_{N_ORDERS // 4}"
    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process(f"cancel {target_id}")
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Cancelar Ordem oculta no meio do Book O(1)  : {(end_t - start_t) * 1_000_000:.2f} microssegundos")

    target_id_mod = f"id_{N_ORDERS // 4 + 1}"
    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process(f"modify {target_id_mod} qty 5")
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Modificar Quantidade da Ordem O(1)          : {(end_t - start_t) * 1_000_000:.2f} microssegundos")

    # Varre 5000 de volume da ponta de venda (Vai destruir exatos 10 níveis de preço inteiros)
    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process("market buy 5000")
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Market Order Gigante (Sweep de 5000 items)  : {(end_t - start_t) * 1_000:.2f} milissegundos")

    print()
    print("---------------------------------------------------------------")
    print(" Dinâmica de Pegged Orders (Testes de Atualização em Massa):")
    print()

    # Prepara 1000 Pegged Orders (que vão ancorar no Best Bid atual que é 100)
    sys.stdout = suppress_stdout()
    for _ in range(1000):
        parser.process("peg bid buy 10") 
    sys.stdout = old_stdout

    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process("peg bid buy 10")
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Inserir 1 Ordem Pegged O(1)                 : {(end_t - start_t) * 1_000_000:.2f} microssegundos")

    # O Best Bid atual é 100. Inserir a 105 melhora o spread sem cruzar.
    # As 1.001 Peggeds subirão instantaneamente para 105.
    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process("limit buy 105 100") 
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Atualizar 1.001 Peggeds (Melhoria de Preço) : {(end_t - start_t) * 1_000_000:.2f} microssegundos")

    # A ordem limite a 105 tem "100" de volume. Vendemos 100 a mercado para consumi-la totalmente.
    # O nível 105 é destruído. O LOB avisa as Peggeds para voltarem para o nível 100.
    sys.stdout = suppress_stdout()
    start_t = time.perf_counter()
    parser.process("market sell 100")
    end_t = time.perf_counter()
    sys.stdout = old_stdout
    print(f"Atualizar 1.001 Peggeds (Fallback de Preço) : {(end_t - start_t) * 1_000_000:.2f} microssegundos")

    print()
    print("===============================================================")

if __name__ == '__main__':
    run_benchmarks()