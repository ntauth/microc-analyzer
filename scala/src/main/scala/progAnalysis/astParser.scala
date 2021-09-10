package progAnalysis

import atto._
import Atto._
import cats.implicits._
import pprint.pprintln

object astParser {

  def pp(x: Any): Unit =
    pprint.pprintln(x, 100, 100000)


  /** We write x for variables, A for array names, R for record names and n for numbers */
  case class Lit(x: String)

  sealed trait Expr

  sealed trait Expr_l extends Expr

  sealed trait Expr_a extends Expr

  sealed trait Expr_b extends Expr

  object Expr {
    case object T extends Expr_b

    case object F extends Expr_b

    case class opR(a: Expr_b, b: Expr_b) extends Expr_b
  }

  sealed trait Stmt

  object Stmt {
    case class Stmts(xs: List[Stmt]) extends Stmt

    case class `:=`(l: Lit, ln: Int, a: Expr) extends Stmt

    case class R(l: Lit, a: Expr_a, b: Expr_a) extends Stmt //tuple

    case class If_(b: Expr_b, ln: Int, s1: Stmt, s2: Stmt) extends Stmt //if

    case class While_(b: Expr_b, ln: Int, s: Stmt) extends Stmt //if

    val stmt1 = If_(Expr.T, 1, `:=`(Lit("a"), 2, Expr.T), `:=`(Lit("b"), 3, Expr.F))
    val stmt1_unnumed = If_(Expr.T, 0, `:=`(Lit("a"), 0, Expr.T), `:=`(Lit("b"), 0, Expr.F))
    val stmt2_numed =
      If_(Expr.T, 1, Stmts(List(`:=`(Lit("a"), 2, Expr.T), `:=`(Lit("a"), 3, Expr.T))), `:=`(Lit("b"), 4, Expr.F))
  }

  def stmtLoc(s: Stmt) = s match {
    case Stmt.`:=`(l, ln, a) => ln
    case _ => -1
    //    case Stmt.Stmts(xs) =>
    //    case Stmt.R(l, a, b) =>
    //    case Stmt.If_(b, ln, s1, s2) =>
    //    case Stmt.While_(b, ln, s) =>
  }

  sealed trait Decl

  object Decl {
    case class int_(l: Lit) extends Decl

    case class intArr(l: Lit, len: Int) extends Decl
  }

  case class Prog(ds: List[Decl], stmts: Stmt.Stmts)

  val litP: Parser[Lit] = many(letter).map(x => Lit(x.mkString))
  //  val declP = stringLiteral.sepBy(char(';'))

  val declIntP: Parser[Decl] = for {
    _ <- skipWhitespace >> string("int") >> skipWhitespace
    l <- litP
  } yield Decl.int_(l)

  val declIntArr: Parser[Decl] = for {
    _ <- string("int[")
    len <- int
    _ <- char(']') >> skipWhitespace
    l <- litP
  } yield Decl.intArr(l, len)

  val progP: Parser[List[Decl]] = for {
    _ <- char('{')
    d <- sepBy(declIntP | declIntArr, char(';'))
    //    _ <- char('}')
    _ <- many(letter) //char('}')
  } yield {
    d
  }

  val progP2 = braces(many(for {
    x <- (declIntArr | declIntP)
    _ <- many(oneOf("\n;"))
  } yield x))

  val microC_decl =
    """{ int i;
      |int[10] A;
      |}""".stripMargin

  val microC1 =
    """{ int i;
      |{int fst; int snd} R;
      |int[10] A;
      |while (i<10)
      |{read A[i]; i:=i+1;
      |}
      |i=0;
      |while (i<10)
      |{if (A[i]>=0)
      |{R.fst := R.fst+A[i]; i := i+1;}
      |else {i := i+1; break;} /* try also with continue */
      |R.snd := R.snd+1;
      |}
      |write R.fst/R.snd;
      |}""".stripMargin

  def numStmt(s: Stmt, i: Int): Stmt = {
    s match {
      case Stmt.Stmts(xs) =>
        xs match {
          case Nil => s
          case ::(head, tl) => Stmt.Stmts(List(numStmt(head, i), numStmt(Stmt.Stmts(tl), i + 1)))
        }
      case x@Stmt.`:=`(l, ln, a) => x.copy(ln = i)
      case x@Stmt.If_(b, ln, s1, s2) => Stmt.If_(b, i, numStmt(s1, i + 1), numStmt(s2, i + 2))
      case _ => s
      //      case Stmt.R(l, a, b)             =>
    }
  }

}
