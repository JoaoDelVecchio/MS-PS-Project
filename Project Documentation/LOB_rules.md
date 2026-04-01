# Regras de Negócio: Limit Order Book (LOB) e Matching Engine

## 1. Regra Geral de Prioridade

A execução segue estritamente a prioridade **Preço-Tempo (FIFO)**:

* **Preço:** Compras com preços maiores (Best Bid) e vendas com preços menores (Best Ask) têm prioridade absoluta.
* **Tempo:** No mesmo preço, a ordem com o menor `seq_id` (mais antiga) é executada primeiro.


## 2. Comportamento por Tipo de Ordem

### 2.1. Limit Orders

* **Agressivas (Cross the Spread):** Se chegam com preço igual ou melhor que o topo oposto, executam imediatamente. O saldo remanescente (se houver) vai para o LOB.
* **Passivas:** Se não cruzam o spread, entram diretamente no LOB para repousar.

### 2.2. Market Orders

* Ordens puramente agressivas (sem preço limite).
* Executam contra a melhor liquidez oposta, varrendo múltiplos níveis de preço até serem totalmente preenchidas ou esvaziarem o LOB.

### 2.3. Pegged Orders

* Ordens dinâmicas ancoradas ao melhor preço limite do seu próprio lado (Best Bid para compra, Best Ask para venda).
* **Atualização Automática:** Se o mercado mudar (por execuções ou cancelamentos), a Pegged ajusta seu preço automaticamente para acompanhar a nova âncora.
* **Manutenção da Prioridade Temporal:** Ao sofrer atualização de preço, a Pegged Order **mantém seu `seq_id` original**. Ela entra na fila do novo preço de acordo com a sua data de criação, ficando à frente de Limit Orders mais recentes.


## 3. Modificações e Cancelamentos

### 3.1. Cancelamento (Cancel)

* Remove a ordem do livro. 
* Se a ordem for a última a sustentar o melhor preço, força a atualização de todas as Pegged Orders ancoradas nela para o nível seguinte.

### 3.2. Modificação (Modify)

Alterações em ordens repousadas seguem regras estritas de prioridade:

* **Reduzir Quantidade:** **Mantém** a prioridade temporal intacta.
* **Aumentar Quantidade:** **Perde** a prioridade temporal (vai para o final da fila do seu preço).
* **Alterar Preço:** **Perde** a prioridade temporal (vai para o final da fila do novo nível de preço).
