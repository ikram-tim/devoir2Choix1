import com.nimbusds.jose.util.StandardCharset
import org.apache.spark.sql.{Encoders, SparkSession}

import scala.collection.mutable.ListBuffer
import play.api.libs.json

import java.nio.file.{Files, OpenOption, Path, Paths}
import scala.reflect.io.File
//alt enter pour les types

object exo2 extends App {

  case class Creature(name: String, spells: Array[String]) {}

  val spark = SparkSession
    .builder()
    .master("local[*]")
    .appName("Spark SQL basic example")
    .config("spark.some.config.option", "some-value")
    .getOrCreate()

  import spark.implicits._

  // pour désactiver les messages des érreurs
  spark.sparkContext.setLogLevel("ERROR")

  // créer un schema spark à partir de la structure de notre class case Creature
  val schema = Encoders.product[Creature].schema

  // la lecture du fichier json et convertion en RDD a partir de la class Creature
  val SortRDD = spark.read.schema(schema).json("src/files/CreaturesAndSpells.json").as[Creature].rdd

  val inver = SortRDD.flatMap(elem => {
    // création d'une liste immutable
    val mapped = new ListBuffer[(String, List[String])]()
    var x = ""
    for (x <- elem.spells) {
      mapped += ((x, List(elem.name)))

    }
    mapped.toList

  })


  val RddIndexInver = inver.reduceByKey(
    (a, b) => {
      var newList: List[String] = a
      for (x <- b) {
        if (!a.contains(x)) {
          newList = x :: a
        }
      }

      newList
    }
  )
  RddIndexInver.collect().foreach(println)

  var collected = Map[String, List[String]]()

  for (x <- RddIndexInver.collect()) {
    collected += x._1 -> x._2
  }

  var jsoned = json.Json.toJson(collected).toString()
  var byted = jsoned.getBytes(StandardCharset.UTF_8)


  Files.write(Paths.get("src/files/SpellsAndCreatures.json"), byted)

  spark.close()

}