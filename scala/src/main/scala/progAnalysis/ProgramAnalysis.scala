package progAnalysis

import atto._
import Atto._
import cats.implicits._
import pprint.pprintln

import astParser._
import flowGraph._

object ProgramAnalysis {


  def run = {
    val brp1 = braces(many(noneOf("{}")))
    val r = progP2.parseOnly(microC_decl) //microC_decl
    pprintln(r)

    pprintln(Stmt.stmt1)
    pprintln(flowG(Stmt.stmt1))

    pprintln(Stmt.stmt2_numed, width = 5)
    pprintln(flowG(Stmt.stmt2_numed))

    pprintln(numStmt(Stmt.stmt1_unnumed, 0))
    /*
    val r1   = (declIntArr | declIntP).parse("int i").done
    val r2   = (declIntArr | declIntP).parse("int[10] A").done
    pprint.pprintln(r1)
    pprint.pprintln(r2)
   */
  }



}
