# 🥖 PaozinhoQuentinho-Py

Um sistema inteligente de notificações de "Pão Quente" via WhatsApp, desenvolvido com **Python**, **FastAPI** e **Evolution API**.

O projeto permite que padarias enviem alertas em massa para uma lista de contatos, oferecendo botões interativos para reserva imediata, garantindo uma melhor experiência para o cliente e agilidade no balcão.

## 🚀 Funcionalidades

- **Disparo em Massa:** Envio programado com intervalos randômicos para evitar banimento.
- **Botões Interativos:** Reserva direta pelo WhatsApp (ex: "Reservar 5 pães").
- **Gestão de Opt-out:** Sistema automático de "Não Perturbe".
- **Confirmação em Tempo Real:** Feedback imediato para o cliente após a reserva.
- **Arquitetura Assíncrona:** Construído sobre FastAPI para alta performance.

## 🛠️ Tech Stack

- **Linguagem:** Python 3.10+
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Engine WhatsApp:** [Evolution API](https://github.com/EvolutionAPI/evolution-api) (Dockerizada)
- **Banco de Dados:** PostgreSQL (SQLAlchemy/Tortoise)
- **Fila/Task Manager:** Redis + Celery (para disparos cadenciados)

## 🏗️ Arquitetura do Sistema

1. **Trigger:** O padeiro aciona o endpoint `/pao-quente`.
2. **Worker:** Uma tarefa é enfileirada no Redis.
3. **Dispatcher:** O worker consome a Evolution API respeitando o delay seguro.
4. **Webhook:** O sistema recebe o clique do usuário e atualiza o banco de dados.
