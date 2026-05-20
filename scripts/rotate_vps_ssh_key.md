# Rotacao de chave SSH da VPS

Runbook manual para trocar acesso por senha por chave SSH. Nao registre senhas neste arquivo.

1. Gere uma chave local dedicada:

   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/one_fianca_vps -C "one-fianca-vps"
   ```

2. Instale a chave publica na VPS ainda usando o acesso atual:

   ```bash
   ssh-copy-id -i ~/.ssh/one_fianca_vps.pub root@SEU_HOST
   ```

3. Valide login com chave em uma nova sessao antes de alterar configuracoes:

   ```bash
   ssh -i ~/.ssh/one_fianca_vps root@SEU_HOST
   ```

4. Na VPS, edite `/etc/ssh/sshd_config` e confirme:

   ```text
   PubkeyAuthentication yes
   PasswordAuthentication no
   PermitRootLogin prohibit-password
   ```

5. Valide a configuracao e recarregue o SSH:

   ```bash
   sshd -t
   systemctl reload ssh
   ```

6. Mantenha a sessao antiga aberta enquanto testa uma nova conexao com chave.

7. Atualize `ops.env` local fora do Git com:

   ```text
   VPS_SSH_KEY_PATH=~/.ssh/one_fianca_vps
   VPS_SSH_USER=root
   VPS_SSH_PORT=22
   ```
