1. Tipos Básicos (Value Objects & Enums)
Estes são objetos imutáveis que apenas carregam dados.

Side (Enum)

Valores: BUY, SELL

Trade (Value Object)

Responsabilidade: Representar um negócio executado. Sendo um Value Object, uma vez criado, não pode ser alterado.

Atributos:

price (Float)

qty (Inteiro)

2. Entidades de Domínio (As Ordens / Nós da Lista)
As ordens agora carregam a responsabilidade de gerenciar seus próprios ponteiros para a lista duplamente encadeada.

Order (Classe Abstrata / Base)

Responsabilidade: Manter a identidade e o estado básico da ordem, além de servir como "Nó" para a fila.

Atributos:

id (String)

side (Side)

qty (Inteiro)

price (Float ou None para Market Orders)

prev (Ponteiro para a Order anterior na fila)

next (Ponteiro para a próxima Order na fila)

Métodos:

reduce_qty(amount): Subtrai a quantidade quando ocorre um trade parcial ou quando o usuário altera a quantidade para baixo. Mantém os ponteiros intactos (preserva a prioridade temporal).

LimitOrder (Herda de Order)

Responsabilidade: Representar uma ordem passiva ou agressiva com preço limite.

Atributos e Métodos: Herda tudo da base. (A lógica de alterar preço de uma Limit será tratada pela Engine recriando a ordem para forçar a perda de prioridade).

PeggedOrder (Herda de Order)

Responsabilidade: Representar a ordem atrelada.

Atributos:

peg_type (Enum: BID ou OFFER)

Métodos:

update_internal_price(new_price): Apenas atualiza o valor do atributo price da entidade. A movimentação estrutural na fila será feita pelo Livro.

MarketOrder (Herda de Order)

Responsabilidade: Representar a agressão imediata. Não vai para o livro, logo seus ponteiros prev e next nunca serão usados.

3. Estruturas Auxiliares (A Fila)
OrderList (A Lista Duplamente Encadeada)

Responsabilidade: Gerenciar a fila FIFO de ordens que compartilham exatamente o mesmo nível de preço.

Atributos:

head (Ponteiro para a primeira Order)

tail (Ponteiro para a última Order)

total_volume (Inteiro: soma das quantidades da fila)

Métodos:

append(Order): Insere a ordem no final (tail). Usado para novas Limit Orders ou Pegged Orders cujo preço piorou. Custo: O(1).

prepend(Order): Insere a ordem no início (head). Usado exclusivamente para Pegged Orders quando o preço de referência melhora (fura-fila). Custo: O(1).

remove(Order): Usa os ponteiros prev e next da própria Order para retirá-la do meio da fila e reconectar os vizinhos. Custo: O(1).

is_empty(): Retorna booleano se a fila secou.

4. Raiz de Agregação (O Livro de Ofertas)
OrderBook

Responsabilidade: Armazenar o estado do mercado, garantir a integridade estrutural das filas e expor dados para a Engine. Não contém regras de negócio de matching.

Atributos:

orders_map (Hash Map: id -> Order): Acesso instantâneo a qualquer ordem.

pegged_bids_map e pegged_asks_map (Hash Maps: id -> PeggedOrder): Rastreamento rápido das ordens dinâmicas.

bids_dict e asks_dict (Hash Maps: price -> OrderList): Mapeia um preço para a sua respectiva fila.

bid_prices e ask_prices (Arrays Ordenados via bisect): Mantém os níveis de preço ordenados.

Métodos:

add_order(Order): Registra nos dicionários e dá append na OrderList correspondente. Se o preço for novo, insere ordenado nos arrays de preço O(log M).

remove_order(Order): Aciona o remove da OrderList, limpa dos dicionários. Se a fila esvaziar, limpa o preço dos arrays.

get_best_bid(): Lê o final do array bid_prices e retorna a OrderList inteira daquele preço.

get_best_ask(): Lê o início do array ask_prices e retorna a OrderList.

update_pegged_orders(side, new_best_price, is_improvement): Itera sobre os mapas de pegged do lado afetado. Tira a ordem da fila atual (remove), atualiza o preço interno, e a insere na nova fila (prepend se is_improvement for true, append se for false).

5. Serviço de Domínio (O Motor)
MatchingEngine

Responsabilidade: Orquestrar o cruzamento (matching), disparar atualizações nas Pegged Orders e ditar o ciclo de vida das ordens perante modificações.

Atributos:

book (Instância de OrderBook)

Métodos:

process_limit_order(LimitOrder):

Compara o preço da Limit com o melhor lado oposto (book.get_best_ask() ou bid()).

Enquanto cruzar o spread e houver liquidez oposta, gera Trade e chama book.remove_order(oposta) ou oposta.reduce_qty().

Se sobrar quantidade, book.add_order(nova_limit).

Verifica se o topo do livro mudou e aciona book.update_pegged_orders().

process_market_order(MarketOrder): Mesma lógica acima, mas consome o book independentemente de preço até zerar a quantidade. Descarta o saldo se o livro secar. Atualiza Peggeds se o topo mudar.

process_pegged_order(PeggedOrder): Consulta o melhor preço atual do próprio lado. Seta o preço da Pegged e a injeta no book via book.add_order().

cancel_order(order_id): Busca no orders_map, verifica de qual lado era. Chama book.remove_order(). Se era o topo do livro, recalcula o novo melhor preço e aciona book.update_pegged_orders(..., is_improvement=False).

modify_order(order_id, new_price, new_qty):

Se diminuiu apenas a qty: Chama order.reduce_qty() (O(1) puro, mantém prioridade).

Se alterou preço ou aumentou qty: Usa a lógica de "Cancelar e Substituir". Aciona cancel_order(order_id) e injeta a ordem recriada como nova no motor. Isso garante nativamente a perda de prioridade na fila sem escrever código extra.

6. Camadas de I/O (Desacopladas do Domínio)
CommandParser

Responsabilidade: Analisar a string de entrada (ex: "limit buy 10 100"), criar as instâncias do tipo correto de Order e passar para a MatchingEngine. Lida com os erros de digitação (typos) e validação de valores negativos.

BookFormatter / Renderer

Responsabilidade: Ler as estruturas bids_dict, asks_dict e os arrays ordenados do OrderBook para desenhar o texto final no terminal de forma exata ao exigido pelo enunciado, sem interferir na lógica matemática do motor.