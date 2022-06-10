1. Install dependencies

    ```bash
    pip install ansible

    # For local installs
    sudo apt install -y sshpass
    ```

2. Create a file called `vars.yml` that looks like

    ```yaml
    passwords:
        grafana_admin_username: 123
        grafana_admin: 123
    ```

3. Generate keys

    ```bash
    cd files
    openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
    ```

4. Run the Ansible playbook to provision the machine

    ```bash
    ansible-playbook -i <ssh remote>, install.yml --extra-vars=@vars.yml

    # For local installs
    ansible-playbook -i <ssh remote>, install.yml --extra-vars=@vars.yml -kK
    ```


## Debugging

```bash
# see why containers aren't up
sudo docker stack ps monitoring --no-trunc

# see grafana logs
sudo docker service logs monitoring_grafana --raw

# log into a container
sudo docker ps  # get id
sudo docker exec -it <ID> /bin/bash
```

