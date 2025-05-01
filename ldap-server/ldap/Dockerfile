FROM bitnami/openldap:latest

LABEL maintainer="aantonmica@gmail.com"

# Variables d'environnement principales
ENV LDAP_ROOT="dc=mycompany,dc=com" \
    LDAP_ADMIN_USERNAME="admin" \
    LDAP_ADMIN_PASSWORD="adminpassword" \
    LDAP_PORT_NUMBER=1389 \
    LDAP_LDAPS_PORT_NUMBER=1636 \
    LDAP_ENABLE_TLS="yes" \
    LDAP_SKIP_DEFAULT_TREE="no"

# Création des répertoires nécessaires
RUN mkdir -p /ldif/custom && \
    mkdir -p /bitnami/openldap/conf/certs && \
    chmod -R 755 /ldif && \
    chown -R 1001:1001 /ldif

# Copie des fichiers de configuration LDIF
COPY ldif/init.ldif /ldif/custom/init.ldif

# Vérification de la syntaxe du fichier LDIF (optionnel)
RUN slapd -Ttest -f /opt/bitnami/openldap/slapd.conf -u openldap -g openldap && \
    ldapadd -Y EXTERNAL -H ldapi:/// -f /ldif/custom/init.ldif -c || (echo "Erreur dans le fichier LDIF"; exit 1)

EXPOSE $LDAP_PORT_NUMBER $LDAP_LDAPS_PORT_NUMBER

CMD ["/opt/bitnami/scripts/openldap/run.sh"]