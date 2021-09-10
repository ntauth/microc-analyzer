package progAnalysis
import progAnalysis.astParser._



object bitVec {

  def genSet(ln: Int, p: Prog): Unit = {}

  def killSet(p: Prog)(s: Stmt): Unit = {
    s match {
      case Stmt.Stmts(xs)          =>
      case Stmt.`:=`(l, ln, a)     =>
      case Stmt.R(l, a, b)         =>
      case Stmt.If_(b, ln, s1, s2) =>
      case Stmt.While_(b, ln, s)   =>
    }
  }

  /** reaching def before */
  def rdPrev(ln: Int) {}

  /** reaching def after */

}
