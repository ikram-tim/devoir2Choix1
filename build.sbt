name := "exo2"

version := "0.1"

scalaVersion := "2.12.15"

updateOptions := updateOptions.value.withCachedResolution(true)

libraryDependencies += "org.apache.spark" %% "spark-sql" % "3.1.2"
libraryDependencies += "org.apache.spark" %% "spark-graphx" % "3.1.2"
libraryDependencies += "com.typesafe.play" %% "play-json" % "2.9.2"