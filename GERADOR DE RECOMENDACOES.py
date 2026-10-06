import os
import re
import logging
from pypdf import PdfReader, PdfWriter

# Configuração de Log para o console do GitHub
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("GeradorRecomendacoes")

# Pastas do repositório
PASTA_PAG1 = "PAG 1"
PASTA_PAG2 = "PAG 2"
PASTA_SAIDA = "Saida"

def iniciar_processamento():
    # Garante que as pastas existam
    os.makedirs(PASTA_PAG1, exist_ok=True)
    os.makedirs(PASTA_PAG2, exist_ok=True)
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    arquivos_pag1 = [arq for arq in os.listdir(PASTA_PAG1) if arq.lower().endswith('.pdf')]
    arquivos_pag2 = [arq for arq in os.listdir(PASTA_PAG2) if arq.lower().endswith('.pdf')]

    total = len(arquivos_pag1)
    if total == 0:
        logger.warning('⚠ Nenhum PDF encontrado na pasta PAG 1.')
        return

    logger.info('=== INICIANDO GERADOR DE RECOMENDAÇÕES ===')
    processados = 0

    for arquivo_pag1 in arquivos_pag1:
        pdf_pag1 = os.path.join(PASTA_PAG1, arquivo_pag1)
        nome_pag1 = os.path.splitext(arquivo_pag1)[0]
        
        correspondentes = []
        # Lógica original de correspondência (Nome exato ou Nome + Q + Números)
        if arquivo_pag1 in arquivos_pag2:
            correspondentes.append(arquivo_pag1)
        else:
            padrao = re.compile(f'^{re.escape(nome_pag1)}Q\\d+\\.pdf$', re.IGNORECASE)
            for arquivo_pag2 in arquivos_pag2:
                if padrao.match(arquivo_pag2):
                    correspondentes.append(arquivo_pag2)
        
        if not correspondentes:
            logger.warning(f'⚠ Correspondência não encontrada: {arquivo_pag1}')
            continue
        
        try:
            reader1 = PdfReader(pdf_pag1)
            if len(reader1.pages) == 0:
                logger.warning(f'⚠ PDF vazio: {arquivo_pag1}')
                continue
            
            primeira_pagina = reader1.pages[0]
            
            for arquivo_pag2 in sorted(correspondentes):
                try:
                    pdf_pag2 = os.path.join(PASTA_PAG2, arquivo_pag2)
                    reader2 = PdfReader(pdf_pag2)
                    writer = PdfWriter()
                    
                    # Adiciona a primeira página da PAG 1
                    writer.add_page(primeira_pagina)
                    
                    # Adiciona todas as páginas da PAG 2
                    for pagina in reader2.pages:
                        writer.add_page(pagina)
                    
                    # Salva na pasta Saída
                    pdf_saida = os.path.join(PASTA_SAIDA, arquivo_pag2)
                    with open(pdf_saida, 'wb') as f:
                        writer.write(f)
                    
                    processados += 1
                    logger.info(f'✔ Gerado: {arquivo_pag2}')
                    
                except Exception as erro_pdf:
                    logger.error(f'❌ Erro em {arquivo_pag2}: {erro_pdf}')
                    
        except Exception as erro_pdf:
            logger.error(f'❌ Erro ao ler {arquivo_pag1}: {erro_pdf}')

    logger.info('==================================================')
    logger.info(f'Arquivos processados com sucesso: {processados}')
    logger.info('==================================================')

if __name__ == '__main__':
    iniciar_processamento()
