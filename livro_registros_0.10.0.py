import sys, os, json, datetime, enum, textwrap
from fpdf import FPDF

if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        DIRETORIO_TRABALHO = sys.argv[1]

else:
    DIRETORIO_TRABALHO = '.'
    #sys.exit('Caminho passado é invalido.')


VER             = '0.9.0'
EXTENCAO        = '.tab'
FORMATO_DATA    = '%d/%m/%y'

TABELA_TRABALHO = None
TABELA_NOME     = None
TABELA_ALVO_MSG = 'Não ha arquivo aberto no momento.\n'


class CONDICAO_REGISTRO(enum.IntEnum):
    Aberto     = 1
    Cancelado  = 2
    Fechado    = 3
    Aguardando = 4


###funções_de_apoio_e_setup


def caminhoParaArquivo(nome):
    return f'{DIRETORIO_TRABALHO}/{nome}{EXTENCAO}'


def setTabelaAlvo():
    global TABELA_ALVO_MSG, COMANDOS
    TABELA_ALVO_MSG = f'Trabalhando no arquivo "{TABELA_NOME}".\n'
    if COMANDOS == COMANDOS_BASE:
        COMANDOS = COMANDOS_REGISTRO


def regua(simbolo='-'):
    print(simbolo * 119)


###funções_de_apoio_e_setup
###operações_de_arquivos


def listarArquivos():
    '''Mostrar os arquivos no diretorio de trabalho.'''
    arquivos = [
            arquivo.removesuffix(EXTENCAO)
            for arquivo in sorted(os.listdir(DIRETORIO_TRABALHO))
            if arquivo.endswith(EXTENCAO)
            ]

    if not arquivos:
        print('Não ha arquivos no diretorio.')
        return 1

    print('Arquivos no diretorio.')
    regua()
    for n, arquivo in enumerate(arquivos, 1):
        if n%8 == 0:
            print(f'{arquivo:16}')

        else:
            print(f'{arquivo:16}|', end='')

    if n%8 != 0:
        print()
    regua()
    print()


def abrir():
    '''Abrir arquivo.'''
    if listarArquivos():
        return

    while True:
        nome = input('Entre o nome do arquivo...\n\t-> ')

        if not nome:
            print('\nOperação cancelada.')
            return

        if not os.path.isfile(caminhoParaArquivo(nome)):
            print(f'\nNão existe arquivo com o nome "{nome}".\n')
            continue

        break

    global TABELA_TRABALHO, TABELA_NOME
    with open(caminhoParaArquivo(nome)) as arquivo:
        TABELA_TRABALHO = json.load(arquivo)
        TABELA_NOME     = nome
    setTabelaAlvo()
    print('\nArquivo aberto.')


def criarArquivo():
    '''Criar arquivo.'''
    while True:
        nome = input('Entre um nome para o arquivo...\n\t-> ')

        if not nome:
            print('\nOperação cancelada.')
            return

        if os.path.isfile(caminhoParaArquivo(nome)):
            print(f'\nJa existe arquivo com o nome "{nome}".\n')
            continue

        break

    base = {
            'ID'        : 0,
            'Registros' : {},
            }

    with open(caminhoParaArquivo(nome), 'w') as arquivo:
        json.dump(base, arquivo)

    global TABELA_TRABALHO, TABELA_NOME
    TABELA_TRABALHO = base
    TABELA_NOME     = nome
    setTabelaAlvo()
    print('\nArquivo criado.')


def salvar():
    '''Salvar arquivo.'''
    with open(caminhoParaArquivo(TABELA_NOME), 'w') as arquivo:
        json.dump(TABELA_TRABALHO, arquivo)

    print('Arquivo salvo.')


###operações_de_arquivos
###operações_de_registro


def listarRegistros(registros):
    print()
    regua()
    if not registros:
        print('Não ha registros com as condições passadas.')

    else:
        print(f"{'ID':^6}|{'Descrição':^76}|{'Valor':^13}|{'Data':^10}| Condição ")
        regua()
        for i_d, registro in registros:
            descricao = textwrap.shorten(registro['descricao'], width=77)
            valor     = f'R${registro["valor"]:>9,.2f}'
            condicao  = CONDICAO_REGISTRO(registro['condicao']).name

            if registro['ultima data'] != None:
                data = datetime.date.fromordinal(registro['ultima data']).strftime(FORMATO_DATA)

            else:
                data = datetime.date.fromordinal(registro['data']).strftime(FORMATO_DATA)

            print(f"{i_d:^6}|{descricao:.<76}|{valor:^13}|{data:^10}|{condicao:>10}")
    regua()


def pesquisarRegistrosCondicao():
    '''Pesquisar por condicão.'''
    while True:
        op = input((
            'Escolha a condição a pesquisar...\n'
            '1 - Aberto\n'
            '2 - Cancelado\n'
            '3 - Fechado\n'
            '4 - Aguardando\n'
            '5 - Todos\n'
            '\t-> '))

        if not op:
            print('\nOperação cancelada.')
            return

        if op == '1':
            op = [CONDICAO_REGISTRO.Aberto]
            break

        elif op == '2':
            op = [CONDICAO_REGISTRO.Cancelado]
            break

        elif op == '3':
            op = [CONDICAO_REGISTRO.Fechado]
            break

        elif op == '4':
            op = [CONDICAO_REGISTRO.Aguardando]
            break

        elif op == '5':
            op = [CONDICAO_REGISTRO.Aberto, CONDICAO_REGISTRO.Cancelado, CONDICAO_REGISTRO.Fechado, CONDICAO_REGISTRO.Aguardando]
            break

        else:
            print('\nCondição invalida...')
            continue

    registros = [
            (i_d, registro)
            for i_d, registro in TABELA_TRABALHO['Registros'].items()
            if registro['condicao'] in op
            ]
    listarRegistros(registros)


def criarRegistro():
    '''Criar registro.'''
    while True:
        descricao = input('Entre uma descrição para o registro...\n\t-> ')

        if not descricao:
            print('\nOperação cancelada.')
            return

        print()
        break

    while True:
        valor = input('Entre um valor para o registro (use . ponto como separador decimal)...\n\t-> R$')

        if not valor:
            print('\nOperação cancelada.')
            return

        try:
            valor = float(valor)

        except ValueError:
            print('\nValor passado é invalido...')
            continue

        print()
        break

    while True:
        data = input('Entre uma data no formato dia/mes/ano ("hoje" usa a data do dia)...\n\t-> ')

        if not data:
            print('\nOperação cancelada.')
            return

        if data == 'hoje':
            data = datetime.date.today().toordinal()
            break

        try:
            data = datetime.datetime.strptime(data, FORMATO_DATA).toordinal()
            break

        except ValueError:
            print('\nData passada é invalida...')
            continue
    print()

    registro = {
            'descricao'     : descricao,
            'valor'         : valor,
            'data'          : data,
            'ultima data'   : None,
            'valor parcial' : 0,
            'condicao'      : CONDICAO_REGISTRO.Aguardando.value
            }

    TABELA_TRABALHO['ID']                     += 1
    id_registro                               = str(TABELA_TRABALHO['ID'])
    TABELA_TRABALHO['Registros'][id_registro] = registro
    print(f'Registro efetuado no ID "{id_registro}".')


def registroPagar():
    '''Fazer pagamento.'''

    registros = [
            (i_d, registro)
            for i_d, registro in TABELA_TRABALHO['Registros'].items()
            if registro['condicao'] == CONDICAO_REGISTRO.Aberto
            ]

    if not registros:
        print('Não ha registros abertos.')
        return

    listarRegistros(registros)

    while True:
        i_d = input('Entre um ID de registro...\n\t-> ')

        if not i_d:
            print('\nOperação cancelada.')
            return

        registro = TABELA_TRABALHO['Registros'].get(i_d)

        if registro == None:
            print(f'\nID "{i_d}" não encontrado na tabela.')
            continue

        if registro['condicao'] != CONDICAO_REGISTRO.Aberto:
            condicao_nome = CONDICAO_REGISTRO(registro['condicao']).name.lower()
            print(f'\nRegistro com ID "{i_d}" esta "{condicao_nome}".')
            continue

        print()
        break

    while True:
        print(f'Valor do registro : R${registro["valor"]:>9,.2f}')
        print(f'Valor em aberto   : R${registro["valor"]-registro["valor parcial"]:>9,.2f}')
        valor = input('Entre um valor para acrescer ao registro (use . ponto como separador decimal)...\n\t-> R$')

        if not valor:
            print('\nOperação cancelada.')
            return

        try:
            valor = float(valor)

        except ValueError:
            print('\nValor passado é invalido.')
            continue

        print()
        break

    registro['valor parcial'] += valor
    registro['ultima data'] = datetime.date.today().toordinal()

    if registro['valor parcial'] >= registro['valor']:
        registro['condicao']   = CONDICAO_REGISTRO.Fechado.value
        registro['valor parcial']    = registro['valor']
        print(f'Registro ID "{i_d}", quitado.')

    else:
        print(f'Registro ID "{i_d}", atualizado.')
    relatorioRegistro(i_d)


def registroCancelar():
    '''Cancelar registro.'''

    registros = [
            (i_d, registro)
            for i_d, registro in TABELA_TRABALHO['Registros'].items()
            if registro['condicao'] == CONDICAO_REGISTRO.Aberto
            ]

    if not registros:
        print('Não ha registros abertos.')
        return

    listarRegistros(registros)

    while True:
        i_d = input('Entre o ID do registro...\n\t-> ')

        if not i_d:
            print('\nOperação cancelada.')
            return

        registro = TABELA_TRABALHO['Registros'].get(i_d)

        if registro == None:
            print(f'\nID "{i_d}" não encontrado na tabela.')
            continue

        if registro['condicao'] == CONDICAO_REGISTRO.Fechado:
            print('\nNão é possivel cancelar um registro ja fechado.')
            continue

        if registro['condicao'] == CONDICAO_REGISTRO.Cancelado:
            print('\nRegistro ja se encontra cancelado.')
            continue

        break

    registro['condicao'] = CONDICAO_REGISTRO.Cancelado.value
    print('\nRegistro cancelado.')


def registroAbrir():
    '''Abrir registro.'''

    registros = [
            (i_d, registro)
            for i_d, registro in TABELA_TRABALHO['Registros'].items()
            if registro['condicao'] in (CONDICAO_REGISTRO.Cancelado, CONDICAO_REGISTRO.Aguardando)
            ]

    if not registros:
        print('Não ha registros cancelados ou aguardando.')
        return

    listarRegistros(registros)

    while True:
        i_d = input('Entre o ID do registro...\n\t-> ')

        if not i_d:
            print('\nOperação cancelada.')
            return

        registro = TABELA_TRABALHO['Registros'].get(i_d)

        if not registro:
            print('\nID não encontrado.')
            continue

        if registro['condicao'] == CONDICAO_REGISTRO.Fechado:
            print('\nNão é possivel abrir um registro ja fechado.')
            continue

        if registro['condicao'] == CONDICAO_REGISTRO.Aberto:
            print('\nRegistro ja se encontra aberto.')
            continue

        break

    registro['condicao'] = CONDICAO_REGISTRO.Aberto.value
    print('\nRegistro aberto.')


def relatorioRegistro(i_d=None):
    '''Relatorio de registro.'''
    if not i_d:
        while True:
            i_d = input('Entre o ID do registro...\n\t-> ')

            if not i_d:
                print('\nOperação cancelada.')
                return

            registro = TABELA_TRABALHO['Registros'].get(i_d)

            if not registro:
                print('\nID não encontrado.')
                continue

            break
    else:
        registro = TABELA_TRABALHO['Registros'].get(i_d)

    data = datetime.date.fromordinal(registro['data']).strftime(FORMATO_DATA)

    if registro['ultima data']:
        data_atualizacao = datetime.date.fromordinal(registro['ultima data']).strftime(FORMATO_DATA)

    else:
        data_atualizacao = '........'

    descricao    = f'Descrição         : {registro["descricao"]}'
    descricao    = textwrap.fill(descricao, subsequent_indent=' '*20, width=119)
    valor_aberto = registro['valor'] - registro['valor parcial'] 

    print()
    regua()
    print((
        '\n'
        f'Identificação(ID) : {i_d}\n'
        '\n'
        f'Data de abertura  : {data}\n'
        f'Data atualização  : {data_atualizacao}\n'
        '\n'
        f'Valor do serviço  : R${registro["valor"]:>10,.2f}\n'
        f'Valores pagos     : R${registro["valor parcial"]:>10,.2f}\n'
        f'Valor em aberto   : R${valor_aberto:>10,.2f}\n'
        '\n'
        f'Condição          : {CONDICAO_REGISTRO(registro["condicao"]).name}\n'
        '\n'
        f'{descricao}'
        '\n'
        f'\nData da consulta  : {datetime.date.today().strftime(FORMATO_DATA)}'
        ))
    regua()


def relatorioMes():
    '''Relatorio do mes.'''
    while True:
        mes = input('Entre uma data no formato mes/ano("hoje" usa o mes atual)...\n\t-> ')

        if not mes:
            print('\nOperação cancelada.')
            return

        if mes == 'hoje':
            mes = datetime.date.today().strftime('%m/%y')

        try:
            mes = datetime.datetime.strptime(mes, '%m/%y').strftime('%m/%y')

        except ValueError:
            print('\nData invalida.')
            continue

        break

    registros = [
            (i_d, registro)
            for i_d, registro in TABELA_TRABALHO['Registros'].items()
            if (datetime.date.fromordinal(registro['data']).strftime('%m/%y') == mes
                and registro['condicao'] != CONDICAO_REGISTRO.Aguardando)
            ]

    abertos       = 0
    fechados      = 0
    cancelados    = 0
    valor_total   = 0
    valor_parcial = 0

    for i_d, registro in registros:
        if registro['condicao'] == CONDICAO_REGISTRO.Aberto:
            abertos += 1
            valor_total += registro['valor']
            valor_parcial += registro['valor parcial']

        elif registro['condicao'] == CONDICAO_REGISTRO.Fechado:
            fechados += 1
            valor_total += registro['valor']
            valor_parcial += registro['valor parcial']

        elif registro['condicao'] == CONDICAO_REGISTRO.Cancelado:
            cancelados += 1

    valor_diferencial = valor_total - valor_parcial

    print()
    regua()
    print((
        '\n'
        f'Relatorio do mes : {mes}\n'
        '\n'
        f'Registros realisados : {len(registros)}\n'
        '\n'
        f'Registros em aberto  : {abertos}\n'
        f'Registros cancelados : {cancelados}\n'
        f'Registros fechados   : {fechados}\n'
        '\n'
        f'Valores totais       : R${valor_total:>10,.2f}\n'
        f'Valores pagos        : R${valor_parcial:>10,.2f}\n'
        f'Valores em aberto    : R${valor_diferencial:>10,.2f}\n'
        ))
    regua()
    print(f'\n{"Relação de serviços":^100}')
    listarRegistros(registros)
    print(f'\nData da consulta : {datetime.date.today().strftime(FORMATO_DATA)}')


def relatorioAno():
    '''Relatorio do ano.'''
    while True:
        ano = input('Entre um ano("hoje" usa o ano atual)...\n\t-> ')

        if not ano:
            print('\nOperação cancelada.')
            return

        if ano == 'hoje':
            ano = datetime.date.today().strftime('%y')

        try:
            ano = datetime.datetime.strptime(ano, '%y').strftime('%y')

        except ValueError:
            print('\nData invalida.')
            continue

        break

    registros = [
            (i_d, registro)
            for i_d, registro in TABELA_TRABALHO['Registros'].items()
            if (datetime.date.fromordinal(registro['data']).strftime('%y') == ano
                and registro['condicao'] != CONDICAO_REGISTRO.Aguardando)
            ]

    abertos       = 0
    fechados      = 0
    cancelados    = 0
    valor_total   = 0
    valor_parcial = 0

    for i_d, registro in registros:
        if registro['condicao'] == CONDICAO_REGISTRO.Aberto:
            abertos += 1
            valor_total += registro['valor']
            valor_parcial += registro['valor parcial']

        elif registro['condicao'] == CONDICAO_REGISTRO.Fechado:
            fechados += 1
            valor_total += registro['valor']
            valor_parcial += registro['valor parcial']

        elif registro['condicao'] == CONDICAO_REGISTRO.Cancelado:
            cancelados += 1

    valor_diferencial = valor_total - valor_parcial

    print()
    regua()
    print((
        '\n'
        f'Relatorio do ano : {ano}\n'
        '\n'
        f'Registros realisados : {len(registros)}\n'
        '\n'
        f'Registros em aberto  : {abertos}\n'
        f'Registros cancelados : {cancelados}\n'
        f'Registros fechados   : {fechados}\n'
        '\n'
        f'Valores totais       : R${valor_total:>10,.2f}\n'
        f'Valores pagos        : R${valor_parcial:>10,.2f}\n'
        f'Valores em aberto    : R${valor_diferencial:>10,.2f}\n'
        ))
    regua()
    print(f'\n{"Relação de serviços":^100}')
    listarRegistros(registros)
    print(f'\nData da consulta : {datetime.date.today().strftime(FORMATO_DATA)}')


###operações_de_registro
###impressão_de_registro


def registroPDF():
    '''Salvar Registro em PDF'''
    while True:
        i_d = input('Entre o ID do registro...\n\t-> ')

        if not i_d:
            print('\nOperação cancelada.')
            return

        registro = TABELA_TRABALHO['Registros'].get(i_d)

        if not registro:
            print('\nID não encontrado.')
            continue

        break

    data = datetime.date.fromordinal(registro['data']).strftime(FORMATO_DATA)

    if registro['ultima data']:
        data_atualizacao = datetime.date.fromordinal(registro['ultima data']).strftime(FORMATO_DATA)

    else:
        data_atualizacao = '........'

    descricao    = registro["descricao"]
    descricao    = textwrap.fill(descricao, width=74)
    valor_aberto = registro['valor'] - registro['valor parcial'] 

    #começar pdf
    caminho = os.path.expanduser(f'~/Elton usinagem - {TABELA_NOME} - {i_d}.pdf')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('helvetica', size=16)
    pdf.cell(text='Elton, serviços de usinagem.')
    pdf.ln(10)
    pdf.cell(text='WhatsApp: (11) 9 5236-3271')
    pdf.ln(10)

    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(10)

    x = 62
    pdf.cell(text='Cliente')
    pdf.set_x(x)
    pdf.cell(text=f': {TABELA_NOME}')
    pdf.ln(10)

    pdf.cell(text='Identificação(ID)')
    pdf.set_x(x)
    pdf.cell(text=f': {i_d}')
    pdf.ln(10)

    pdf.cell(text='Data de abertura')
    pdf.set_x(x)
    pdf.cell(text=f': {data}')
    pdf.ln(10)

    pdf.cell(text='Data de atualização')
    pdf.set_x(x)
    pdf.cell(text=f': {data_atualizacao}')
    pdf.ln(10)

    pdf.cell(text='Valor do serviço')
    pdf.set_x(x)
    pdf.cell(text=f': R$ {registro["valor"]:.2f}')
    pdf.ln(10)

    pdf.cell(text='Valores pagos')
    pdf.set_x(x)
    pdf.cell(text=f': R$ {registro["valor parcial"]:.2f}')
    pdf.ln(10)

    pdf.cell(text='Valor em aberto')
    pdf.set_x(x)
    pdf.cell(text=f': R$ {valor_aberto:.2f}')
    pdf.ln(10)

    pdf.cell(text='Condição')
    pdf.set_x(x)
    pdf.cell(text=f': {CONDICAO_REGISTRO(registro["condicao"]).name}\n')
    pdf.ln(10)

    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(10)

    pdf.cell(text='Descrição do serviço')
    pdf.ln(10)

    for d in descricao.split('\n'):
        pdf.cell(text=d)
        pdf.ln(10)


    pdf.output(caminho)

    print(f'\nSalvo em : {caminho}')


###impressão_de_registro


COMANDOS_BASE = {
        '1' : abrir,
        '2' : criarArquivo,
        }

COMANDOS_REGISTRO = {
        **COMANDOS_BASE,
        '3'  : salvar,
        '4'  : pesquisarRegistrosCondicao,
        '5'  : criarRegistro,
        '6'  : registroPagar,
        '7'  : registroCancelar,
        '8'  : registroAbrir,
        '9'  : relatorioRegistro,
        '10' : relatorioMes,
        '11' : relatorioAno,
        '12' : registroPDF,
        }

COMANDOS = COMANDOS_BASE


def menu():
    regua('_')

    while True:
        print(f'\n{TABELA_ALVO_MSG}')
        for n, comando in COMANDOS.items():
            if n in ('4', '9', '12'):
                print()

            print(f'{n:>2} - {comando.__doc__}')

        opcao = input('\n => ')
        if not opcao:
            print('\nSessão encerrada.')
            break

        comando = COMANDOS.get(opcao)
        if comando == None:
            print('\nEscolha não encontrada.')

        else:
            print()
            comando()
        input('Enter para continuar...')
        regua('_')
    regua('_')
    print()


if __name__ == '__main__':
    menu()

