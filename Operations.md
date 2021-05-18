# Operations

## Initial deployment to k8s

Create secrets:

```bash
kubectl create secret generic shipanaro-secrets \
 --from-literal database_url="postgres://shipanaro:${POSTGRESS_PASSWORD}@postgres-postgresql/shipanaro" \
 --from-literal secret_key="${SECRET_KEY}" \
 --from-literal email_url='console://'

kubectl create secret generic ldap-secrets \
 --from-literal url='ldap://openldap' \
 --from-literal user_dn='cn=admin,dc=pirata,dc=cat' \
 --from-literal password="${LDAP_ADMIN_PASSWORD}"
```

Deploy all resources:

    kubectl apply -f k8s

...wait until everything is up:

    kubectl get pods -w

Connect to ldapadmin using port forwarding:

    kubectl port-forward service/ldapadmin 7777:https

(browse to https://localhost:7777 to log in to the LDAP admin)
