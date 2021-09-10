package progAnalysis

import astParser._

object flowGraph {

  def initSet(s: Stmt): Stmt = {
    s match {
      case Stmt.Stmts(xs) => xs.head
      case x => x

    }
  }

  def finalSet(s: Stmt): List[Stmt] = s match {
    case Stmt.Stmts(xs) => xs.reverse.headOption.toList
    case Stmt.If_(b, ln, s1, s2) => List(s1, s2)
    case x => List(x)
    //    case Stmt.`:=`(l, ln, a) =>
    //    case Stmt.R(l, a, b) =>
  }

  def flowG(s: Stmt): List[(Int, Int)] = s match {
    case Stmt.If_(b, bln, s1, s2) =>
      flowG(s1) ++ flowG(s2) ++ List((bln, stmtLoc(initSet(s1))), (bln, stmtLoc(initSet(s2))))
    case x@Stmt.While_(b, ln, s) =>
      List((stmtLoc(x), stmtLoc(initSet(s)))) ++ flowG(s) ++ finalSet(s).map(ss => (stmtLoc(ss), stmtLoc(s)))
    case Stmt.Stmts(xs) =>
      xs match {
        case s1 :: s2 :: ss =>
          flowG(s1) ++ flowG(Stmt.Stmts(s2 :: ss)) ++ finalSet(s1).map(s => (stmtLoc(s), stmtLoc(s2)))
        case _ => List.empty
      }
    case _ => List()
  }

}
