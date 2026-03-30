Esta documentação detalha a complexidade de tempo da arquitetura atual do motor de correspondência (Matching Engine), baseada na notação Big-O. O modelo desenhado utiliza uma combinação de **Tabelas de Dispersão (Hash Maps)**, **Listas Duplamente Ligadas (Doubly Linked Lists)** e **Arrays Ordenados (Sorted Arrays via Bisect)**.

Para a análise, definiremos as seguintes variáveis de escala:
* **$L$**: Número de *Limit Orders* ativas no livro.
* **$P$**: Número de *Pegged Orders* de um lado específico do livro.
* **$M$**: Número de níveis de preço distintos no livro (Price Levels). Geralmente, $M \ll L$.
* **$K$**: Número de ordens "descansadas" (resting orders) que são consumidas (swept) por uma única ordem agressiva.
* **$N_{nivel}$**: Número de ordens num único nível de preço.

---

### 1. Documentação da Ordem de Execução (Complexidade de Tempo)

#### 1.1 Limit Buy / Limit Sell
Uma ordem passiva que entra no livro, ou uma ordem agressiva que consome liquidez e deixa o remanescente no livro.
* **Melhor Caso $\mathcal{O}(1)$**: A ordem é passiva, não cruza o *spread*, e o preço especificado já existe no livro de ofertas. A inserção no dicionário (`bids_dict`) é $\mathcal{O}(1)$ e a inserção na lista duplamente ligada (`insert_sorted`), sendo a ordem mais recente, entra no final da fila sem iterações em $\mathcal{O}(1)$. O radar valida os preços em $\mathcal{O}(1)$.
* **Caso Mais Recorrente $\mathcal{O}(1)$ a $\mathcal{O}(M)$**: Num mercado líquido, a maioria das ordens vai para níveis de preço já existentes $\mathcal{O}(1)$. Se criar um nível de preço novo, o `bisect.insort` demora $\mathcal{O}(M)$ para manter o array de preços ordenado.
* **Pior Caso $\mathcal{O}(K + M + P \times N_{nivel})$**: A ordem é extremamente agressiva. Ela consome $K$ ordens do lado oposto ($\mathcal{O}(K)$), remove níveis de preço vazios ($\mathcal{O}(M)$ do array array) e estaciona num novo topo. Ao alterar a âncora de preço do livro, o radar dispara o `update_pegged_orders`. O sistema move $P$ ordens *Pegged* para o novo preço. Como as ordens *Pegged* têm um `seq_id` mais antigo, o `insert_sorted` pode ter de percorrer $N_{nivel}$ ordens para encontrar a prioridade temporal correta.

#### 1.2 Market Buy / Market Sell
Ordens puramente agressivas que varrem o livro até serem preenchidas ou o livro esvaziar.
* **Melhor Caso $\mathcal{O}(1)$**: A ordem é pequena e consome apenas a primeira ordem no topo do livro, sem esvaziar o nível de preço nem alterar a âncora.
* **Caso Mais Recorrente $\mathcal{O}(K)$**: A ordem consome $K$ ordens no topo. A remoção de cada ordem via Dicionário + Lista Duplamente Ligada é estritamente $\mathcal{O}(1)$ por ordem cruzada.
* **Pior Caso $\mathcal{O}(K + M + P \times N_{nivel})$**: Varre múltiplos níveis de preço. Consome $K$ ordens, remove níveis do array `bids_prices` com $\mathcal{O}(M)$ e, ao alterar o melhor limite, despoleta o recálculo e a reinserção de $P$ ordens *Pegged*, que procuram o seu lugar na fila temporal em $\mathcal{O}(N_{nivel})$.

#### 1.3 Peg Bid Buy / Peg Offer Sell
Ordens passivas que se atrelam ao melhor preço limite existente.
* **Melhor Caso / Caso Mais Recorrente $\mathcal{O}(1)$**: O método `get_best_limit_bid_price` lê o topo do array de preços e encontra uma ordem limite imediatamente. O nível de preço já existe no livro. Inserção na Hash Map $\mathcal{O}(1)$, inserção na Linked List $\mathcal{O}(1)$.
* **Pior Caso $\mathcal{O}(M)$**: O topo do mercado tem níveis de preço vazios ou corrompidos, obrigando o `get_best_limit_bid_price` a percorrer $M$ níveis para encontrar uma âncora válida (cenário raro).

#### 1.4 Cancel
Cancelamento de uma ordem em repouso no livro, dado o seu ID.
* **Melhor Caso / Caso Mais Recorrente $\mathcal{O}(1)$**: A ordem encontra-se no meio do livro. Aceder ao `orders_map` demora $\mathcal{O}(1)$. Remover o nó da `OrderDoubleLinkedList` demora $\mathcal{O}(1)$ (basta remapear os ponteiros `prev` e `next`). O radar verifica o topo do livro $\mathcal{O}(1)$ e nota que nada mudou.
* **Pior Caso $\mathcal{O}(M + P \times N_{nivel})$**: A ordem cancelada era a única que suportava o melhor nível de preço do mercado. O nível é apagado do array $\mathcal{O}(M)$. O radar deteta a mudança de spread e obriga à atualização de todas as $P$ ordens *Pegged*.

#### 1.5 Modify
Alteração dos parâmetros de uma ordem existente.
* **Melhor Caso / Caso Mais Recorrente $\mathcal{O}(1)$**: O utilizador apenas reduz a quantidade. A arquitetura atual intercepta esta intenção e simplesmente deduz o volume do objeto `Order` em memória, mantendo a prioridade na fila perfeitamente intacta.
* **Pior Caso $\mathcal{O}(K + M + P \times N_{nivel})$**: O utilizador altera o preço para um nível agressivo que cruza o spread. A ordem antiga é cancelada em $\mathcal{O}(1)$ e a nova interage como uma *Limit Order* agressiva, recaindo no pior caso de "Limit Order" descrito em 1.1.

---

### 2. Comparativo: Dicionários + Listas Ligadas vs. Filas de Prioridade (Priority Queues / Heaps)

Na literatura académica clássica, é comum sugerir o uso de **Max-Heaps** para *Bids* e **Min-Heaps** para *Asks*. No entanto, a arquitetura construída no seu projeto (Hash Maps por preço mapeando para Listas Duplamente Ligadas) é o padrão da indústria financeira (HFT e corretoras) por motivos cruciais de desempenho.

#### Por que a arquitetura atual vence as Priority Queues?

1.  **Inserção (Limit Orders Passivas):**
    * **Heap:** Inserir um elemento numa Heap de $N$ ordens custa sempre $\mathcal{O}(\log N)$, porque é necessário reequilibrar a árvore. Se houver 1 milhão de ordens, a inserção é custosa.
    * **Atual:** Inserir num nível de preço existente custa $\mathcal{O}(1)$. Como a vasta maioria das ordens de HFT é submetida num número restrito de níveis de preço ativos perto do *spread*, o $M$ é minúsculo e as inserções são cirúrgicas e instântaneas.
2.  **Cancelamento (A Operação Mais Frequente no Mercado):**
    * **Heap:** Remover uma ordem aleatória pelo seu ID numa Priority Queue é trágico. Requer uma pesquisa $\mathcal{O}(N)$ para encontrar a ordem, seguida de $\mathcal{O}(\log N)$ para extrair o nó e reequilibrar.
    * **Atual:** O acesso via `orders_map` encontra o nó na memória instantaneamente $\mathcal{O}(1)$. Como é uma Lista Duplamente Ligada, o nó possui ponteiros diretos para os seus vizinhos (`prev` e `next`). A remoção ocorre em $\mathcal{O}(1)$ absoluto, sem deslocar nenhum outro elemento. Num mercado onde 90% das ordens são canceladas antes de serem executadas, esta é a métrica mais importante do sistema.
3.  **Prioridade Temporal Estrita (FIFO):**
    * **Heap:** Para Heaps garantirem a prioridade de tempo de ordens no mesmo preço, exigem lógicas secundárias pesadas.
    * **Atual:** A Lista Ligada preserva nativamente a prioridade temporal. A cabeça (`head`) é sempre a mais antiga a ser executada.
4.  **Agregação de Dados para Market Data:**
    * **Heap:** Saber o volume total a R$ 20.00 exige iterar a árvore toda procurando os nós com esse preço.
    * **Atual:** Basta iterar os nós dentro da lista atrelada à chave de preço da Hash Map, ou até mesmo adicionar um contador `total_qty` dentro da lista encadeada para ter essa informação em $\mathcal{O}(1)$ no futuro.