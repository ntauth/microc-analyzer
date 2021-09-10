ThisBuild / scalaVersion := "2.12.12"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "com.example"
ThisBuild / organizationName := "example"

lazy val root = (project in file("."))
  .settings(
    name := "scala",
    libraryDependencies ++= Seq(
      "org.tpolecat" %% "atto-core" % "0.7.2",
      "com.lihaoyi" %% "pprint" % "0.5.3"
    )
  )

// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for instructions on how to publish to Sonatype.
