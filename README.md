# RentCar
## Projecto Final do Curso de Python

### Luxury Wheels (empresa de aluguer de carros)

Proposta A:
Desenvolver um website ondes os clientes deverão executar as seguintes funcionalidades:
1.  Os clientes têm que registar-se e autenticar-se no website.
2.  Poder efetuar uma pesquisa dos veiculos (carro ou moto) pelo modelo e marca;
        A pesquiza deve possuir filtro de:
            -A Categoria: Pequeno, Médio, Grande, SUV, Luxo
            -Transmissão: Automatico, Manual
            -Tipo de veículo: Carro, Moto
            -Valor da diária
            -Quantidade de Pessoas: 1-4, 5-6, mais de 7
3.  Para fazer a reserva de um veiculo deve-se informar a data de inicio e fim de aluguer;
4.  Escolher a forma de Pagamento e concluir a reserva;
5.  Alterações de reserva será permitida somente para as datas de inicio e fim ou o cancelamento total.

Critérios Técnicos:
1.  Todas as informações necessarias para o projecto devem estar em base de dados em SQL:
    a. Veículos;
    b. Clientes;
    c. Reservas;
    d. Formas de pagamento;
2.  Todas as informações dos veículos devem estar na base de dados, tais como: marca, modelo, categoria, transmissão, tipo de veículo,
    quantidade de pessoas, endereço da imagem do veiculo, valor da diária, data da ultima revisão, data da proxima revisão, data da
    ultima inspeção obrigatoria e etc;
3.  Durante o processo de reserva, o website deve mostrar o valor total da reserva com base no vaor da diária do veículo e a
    quantidade de dias que o cliente escolheu.
4.  Após a reserva ser concluida, o veiculo escolhido não deve ficar mais disponivel para os clientes;
5.  Os veículos também devem ficar indisponiveis caso a data da ultima inspeção obrigatoria seja maior que 1 ano ou caso a data da
    proxima revisão seja inferior do que a actual;

--------------------------------------------------------------
# #############################################################
--------------------------------------------------------------
Proposta B:
Desenvolver uma aplicação para gerir a frota de veículos da empresa e executar as seguintes funcionalidades:
1.  Manter (registar, alterar, listar, remover) os veículos, clientes, reservas e formas de pagamento.
2.  Exportar as informações Excel ou CSV dos veiculos, clientes, reservas e formas de pagamento.
3.  Dashboard inicial com as informações(gráficos e relatorio):
        -Veículos alugados, e a quantidade de dias ainda resta da reserva;
        -Últimos clientes registados;
        -Quantidade de veículos disponiveis, por tipo e categoria;
        -Reservas do mês e o total financeiro;
        -Veículos com a Data da proxima revisão a expirar(15 dias);
        -Veiculos com data da inspeção obrigatória a expirar(15 dias).

Critérios Técnicos:
1.  Todas as informações necessárias para o projeto deve estar em bases de dados em SQL:
    a. Veículos;
    b. Clientes;
    c. Reservas;
    d. Formas de pagamento;
2.  Todas as informações dos veículos devem estar na base de dados, tais como: marca, modelo, categoria, transmissão, tipo de veículo,
    quantidade de pessoas, endereço da imagem do veiculo, valor da diária, data da ultima revisão, data da proxima revisão, data da
    ultima inspeção obrigatoria e etc;
3.  O sistema deve alertar ao gestor que os veículos precisarão de revisão 5 dias antes da data da proxima revisão.
4.  O gestor da frota deve ter a opção de indicar que o veículo está em manutenção e o mesmo ficará indisponivel para alugar;


***
### commands:  
criar o requirements.txt

    pip freeze > requirements.txt

