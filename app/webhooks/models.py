import os
from django.db import models
from shopify_sites.models import ShopifySite
from shopify_sites.graphql import GraphQL,GraphQlIterable,GqlReturn
from slugify import slugify

# Create your models here.

class WebhookDefinition(models.Model):
    topics = [
        ('APP_UNINSTALLED','APP_UNINSTALLED'),
        ('APP_SUBSCRIPTIONS_UPDATE','APP_SUBSCRIPTIONS_UPDATE'),
        ('CARTS_CREATE','CARTS_CREATE'),
        ('CARTS_UPDATE','CARTS_UPDATE'),
        ('CHECKOUTS_CREATE','CHECKOUTS_CREATE'),
        ('CHECKOUTS_DELETE','CHECKOUTS_DELETE'),
        ('CHECKOUTS_UPDATE','CHECKOUTS_UPDATE'),
        ('COMPANIES_CREATE','COMPANIES_CREATE'),
        ('COMPANIES_DELETE','COMPANIES_DELETE'),
        ('COMPANIES_UPDATE','COMPANIES_UPDATE'),
        ('COMPANY_CONTACTS_CREATE','COMPANY_CONTACTS_CREATE'),
        ('COMPANY_CONTACTS_DELETE','COMPANY_CONTACTS_DELETE'),
        ('COMPANY_CONTACTS_UPDATE','COMPANY_CONTACTS_UPDATE'),
        ('CUSTOMERS_CREATE','CUSTOMERS_CREATE'),
        ('CUSTOMERS_DATA_REQUEST','CUSTOMERS_REDACT'),
        ('CUSTOMER_ACCOUNT_SETTINGS_UPDATE','CUSTOMER_ACCOUNT_SETTINGS_UPDATE'),
        ('CUSTOMERS_ENABLE','CUSTOMERS_ENABLE'),
        ('CUSTOMERS_UPDATE','CUSTOMERS_UPDATE'),
        ('CUSTOMERS_EMAIL_MARKETING_CONSENT_UPDATE','CUSTOMERS_EMAIL_MARKETING_CONSENT_UPDATE'),
        ('DRAFT_ORDERS_CREATE','DRAFT_ORDERS_CREATE'),
        ('DRAFT_ORDERS_UPDATE','DRAFT_ORDERS_UPDATE'),
        ('DRAFT_ORDERS_DELETE','DRAFT_ORDERS_DELETE'),
        ('FULFILLMENTS_CREATE','FULFILLMENTS_CREATE'),
        ('FULFILLMENTS_UPDATE','FULFILLMENTS_UPDATE'),
        ('FULFILLMENTS_DELETE','FULFILLMENTS_DELETE'),
        ('INVENTORY_LEVELS_UPDATE','INVENTORY_LEVELS_UPDATE'),
        ('METAOBJECTS_CREATE','METAOBJECTS_CREATE'),
        ('METAOBJECTS_DELETE','METAOBJECTS_DELETE'),
        ('METAOBJECTS_UPDATE','METAOBJECTS_UPDATE'),
        ('ORDER_TRANSACTIONS_CREATE','ORDER_TRANSACTIONS_CREATE'),
        ('ORDERS_CANCELLED','ORDERS_CANCELLED'),
        ('ORDERS_CREATE','ORDERS_CREATE'),
        ('ORDERS_DELETE','ORDERS_DELETE'),
        ('ORDERS_EDITED','ORDERS_EDITED'),
        ('ORDERS_FULFILLED','ORDERS_FULFILLED'),
        ('ORDERS_PAID','ORDERS_PAID'),
        ('ORDERS_UPDATED','ORDERS_UPDATED'),
        ('PRODUCTS_CREATE','PRODUCTS_CREATE'),
        ('PRODUCTS_UPDATE','PRODUCTS_UPDATE'),
        ('PRODUCTS_DELETE','PRODUCTS_DELETE'),
        ('SUBSCRIPTION_BILLING_CYCLES_SKIP','SUBSCRIPTION_BILLING_CYCLES_SKIP'),
        ('SUBSCRIPTION_BILLING_CYCLES_UNSKIP','SUBSCRIPTION_BILLING_CYCLES_UNSKIP'),
        ('SUBSCRIPTION_BILLING_ATTEMPTS_CHALLENGED','SUBSCRIPTION_BILLING_ATTEMPTS_CHALLENGED'),
        ('SUBSCRIPTION_BILLING_ATTEMPTS_FAILURE','SUBSCRIPTION_BILLING_ATTEMPTS_FAILURE'),
        ('SUBSCRIPTION_BILLING_ATTEMPTS_SUCCESS','SUBSCRIPTION_BILLING_ATTEMPTS_SUCCESS'),
        ('SUBSCRIPTION_CONTRACTS_ACTIVATE','SUBSCRIPTION_CONTRACTS_ACTIVATE'),
        ('SUBSCRIPTION_CONTRACTS_CANCEL','SUBSCRIPTION_CONTRACTS_CANCEL'),
        ('SUBSCRIPTION_CONTRACTS_CREATE','SUBSCRIPTION_CONTRACTS_CREATE'),
        ('SUBSCRIPTION_CONTRACTS_EXPIRE','SUBSCRIPTION_CONTRACTS_EXPIRE'),
        ('SUBSCRIPTION_CONTRACTS_FAIL','SUBSCRIPTION_CONTRACTS_FAIL'),
        ('SUBSCRIPTION_CONTRACTS_PAUSE','SUBSCRIPTION_CONTRACTS_PAUSE'),
        ('SUBSCRIPTION_CONTRACTS_UPDATE','SUBSCRIPTION_CONTRACTS_UPDATE')
    ]
    label = models.CharField(max_length=255,default="")
    topic = models.CharField(max_length=128,choices=topics,null=False)
    path = models.CharField(max_length=255,null=False)
    automaticInstall = models.BooleanField(default=True,verbose_name="Install Automatically")

class Webhook(models.Model):
    site = models.ForeignKey(to=ShopifySite,on_delete=models.CASCADE,related_name="webhooks")
    topic = models.ForeignKey(to=WebhookDefinition,on_delete=models.DO_NOTHING)
    shopfiyId = models.CharField(max_length=128)
    path = models.CharField(max_length=128,default="")
    def install(self):
        webhook = GraphQL().run(
            """
            mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
                webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
                    webhookSubscription {
                        id
                        topic
                        filter
                        uri
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
            """,
            {
                "topic": self.topic,
                "webhookSubscription": {
                    "uri": f"{os.environ.get("APP_HOST")}/{self.path}",
                    "filter": "type:lookbook"
                }
            }
        )

        webhookId = webhook.search("data.webhookSubscriptionCreate.webhookSubscription.id")
        if webhookId:
            self.shopfiyId = webhookId
            self.save()
        

        pass

    def uninstall(self):
        GraphQL().run(
            """
            mutation webhookSubscriptionDelete($id: ID!) {
            webhookSubscriptionDelete(id: $id) {
                userErrors {
                field
                message
                }
                deletedWebhookSubscriptionId
            }
            }
            """,
            {}
        )
        pass

class WebhookRequest(models.Model):
    webhookId = models.CharField(max_length=255)
    

    

