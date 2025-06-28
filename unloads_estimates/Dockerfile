FROM registry.fedoraproject.org/fedora:38

COPY requirements.txt /tmp/
RUN dnf install -y dnf-plugins-core && \
    dnf config-manager --add-repo https://rpm.releases.hashicorp.com/fedora/hashicorp.repo && \
    dnf -y install python-pip vault git && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    dnf clean all && \
    curl https://certs.corp.redhat.com/certs/2015-IT-Root-CA.pem > /tmp/cert.pem && \
    setcap cap_ipc_lock= /usr/bin/vault && \
    ln -s /usr/bin/python3 /usr/bin/python
# ENTRYPOINT [ "sudo rm -f /home/gitlab-runner/.bash_logout" ]
