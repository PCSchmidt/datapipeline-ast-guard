from pyspark.sql import functions as F, SparkSession

# Create a SparkSession
spark = SparkSession.builder.appName("MRR_by_Plan").getOrCreate()

# Join users and subscriptions on the user_id
joined_users_subscriptions_df = users_df.join(subscriptions_df, on="user_id", how="inner")

# Join the resulting dataframe with invoices on the subscription_id
joined_users_subscriptions_invoices_df = joined_users_subscriptions_df.join(invoices_df, on="subscription_id", how="left")

# Filter rows where invoice_date is not null (active subscriptions)
active_subscriptions_df = joined_users_subscriptions_invoices_df.filter(F.col("invoice_date").isNotNull())

# Compute the MRR by plan
mrr_by_plan_df = active_subscriptions_df.groupBy("plan").agg(
    F.sum("invoice_amount").alias("mrr")
)

# Order the results by MRR in descending order
mrr_by_plan_df = mrr_by_plan_df.orderBy(F.col("mrr").desc())

# Show the top 10 MRR plans
mrr_by_plan_df.show()

# Save the result to a CSV file
mrr_by_plan_df.coalesce(1).write.csv("mrr_by_plan.csv", header=True, mode="overwrite")
