from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, col

# set conf
conf = (
SparkConf()
    .set("spark.hadoop.fs.s3a.fast.upload", True)
    .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .set('spark.hadoop.fs.s3a.aws.credentials.provider', 'com.amazonaws.auth.EnvironmentVariableCredentialsProvider')
    .set('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:2.7.3')
)

# apply config
sc = SparkContext(conf=conf).getOrCreate()
    

if __name__ == "__main__":

    # init spark session
    spark = SparkSession\
            .builder\
            .appName("ENEM Job")\
            .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    df = (
        spark
        .read
        .format("parquet")
        .load("s3a://dl-processing-zone-539445819062/enem/")
    )
    
    print("****************")
    print("* AGREGA SEXO *")
    print("****************")

    uf_m = (
        df
        .where("TP_SEXO = 'M'")
        .groupBy("SG_UF_RESIDENCIA")
        .agg(count(col("TP_SEXO")).alias("count_m"))
    )

    uf_f = (
        df
        .where("TP_SEXO = 'F'")
        .groupBy("SG_UF_RESIDENCIA")
        .agg(count(col("TP_SEXO")).alias("count_f"))
    )

    uf_sexo = uf_m.join(uf_f, on="SG_UF_RESIDENCIA", how="inner")

    (
        uf_sexo
        .write
        .mode("overwrite")
        .format("parquet")
        .save("s3a://dl-processing-zone-539445819062/intermediarias/uf_sexo")
    )

    print("*********************")
    print("Escrito com sucesso!")
    print("*********************")

    spark.stop()
    