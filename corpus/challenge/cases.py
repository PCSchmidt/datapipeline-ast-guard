"""Constructed challenge set C (docs/PROTOCOL.md).

Each case is a short snippet written from the rule definitions in the protocol, BEFORE the tool was run on it.
A `# expect: RULE` marker on a line means a finding of that rule belongs on that line; a snippet with no marker
should produce no findings at all. `hard=True` marks cases I expected the tool to get wrong in advance (with the
reason). `unclear=True` marks cases where I could not decide the right answer; they are reported but not scored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MARK = re.compile(r"#\s*expect:\s*([A-Z0-9, ]+)")


@dataclass(frozen=True)
class Case:
    id: str
    rule: str  # the rule the case is about (AG000 for parse failures)
    form: str  # the surface form being tested
    code: str
    hard: str = ""  # non-empty: expected in advance to be a known tool limitation (the reason)
    unclear: bool = False

    def expected(self) -> set[tuple[str, int]]:
        out: set[tuple[str, int]] = set()
        for lineno, line in enumerate(self.code.splitlines(), start=1):
            m = MARK.search(line)
            if m:
                for rule in m.group(1).replace(" ", "").split(","):
                    out.add((rule, lineno))
        return out


def c(id: str, rule: str, form: str, code: str, hard: str = "", unclear: bool = False) -> Case:
    return Case(id, rule, form, code.strip("\n") + "\n", hard, unclear)


CASES: list[Case] = [
    # ---------------------------------------------------------------- AG001: unbounded materialisation
    c("A1-01", "AG001", "direct", "rows = df.collect()  # expect: AG001"),
    c("A1-02", "AG001", "direct", "pdf = df.toPandas()  # expect: AG001"),
    c("A1-03", "AG001", "direct", "pdf = df.to_pandas()  # expect: AG001"),
    c("A1-04", "AG001", "chain", 'out = df.filter(df.x > 1).groupBy("k").count().collect()  # expect: AG001'),
    c("A1-05", "AG001", "multiline-chain", 'out = (  # expect: AG001\n    df.filter(df.x > 1)\n    .select("k")\n    .collect()\n)'),
    c("A1-06", "AG001", "chain", 'rows = spark.read.parquet("data/x").select("a").collect()  # expect: AG001'),
    c("A1-07", "AG001", "polars-lazy", 'frame = lf.filter(pl.col("a") > 1).collect()  # expect: AG001'),
    c("A1-08", "AG001", "polars-lazy", 'frame = pl.scan_parquet("data/x").collect(streaming=True)  # expect: AG001'),
    c("A1-09", "AG001", "in-function", "def run(df):\n    return df.collect()  # expect: AG001"),
    c("A1-10", "AG001", "in-comprehension", "names = [r.name for r in df.collect()]  # expect: AG001"),
    c("A1-11", "AG001", "in-loop", "for row in df.collect():  # expect: AG001\n    handle(row)"),
    c("A1-12", "AG001", "in-call", "print(df.collect())  # expect: AG001"),
    c("A1-13", "AG001", "in-call", "n = len(df.collect())  # expect: AG001"),
    c("A1-14", "AG001", "in-lambda", "f = lambda d: d.toPandas()  # expect: AG001"),
    c("A1-15", "AG001", "in-method", "class Job:\n    def run(self, df):\n        return df.toPandas()  # expect: AG001"),
    c("A1-16", "AG001", "non-bounder-in-chain", "rows = df.cache().collect()  # expect: AG001"),
    c("A1-17", "AG001", "non-bounder-in-chain", 'rows = df.orderBy("x").collect()  # expect: AG001'),
    c("A1-18", "AG001", "chain", 'pdf = df.select("a").toPandas()  # expect: AG001'),
    c("A1-19", "AG001", "sql", 'rows = spark.sql("select 1").collect()  # expect: AG001'),
    c("A1-20", "AG001", "index-after", "first = df.collect()[0]  # expect: AG001"),
    c("A1-21", "AG001", "rdd", "vals = df.rdd.collect()  # expect: AG001"),
    c("A1-22", "AG001", "rdd", "vals = df.rdd.map(f).collect()  # expect: AG001"),
    c("A1-23", "AG001", "bound-after", "top = df.toPandas().head()  # expect: AG001"),
    c("A1-24", "AG001", "in-fstring", 'msg = f"{df.toPandas()}"  # expect: AG001'),
    c("A1-25", "AG001", "conditional", "x = df.collect() if flag else []  # expect: AG001"),
    c("A1-26", "AG001", "in-with", 'with open("out.txt") as fh:\n    rows = df.collect()  # expect: AG001'),
    c("A1-27", "AG001", "main-block", 'if __name__ == "__main__":\n    rows = df.collect()  # expect: AG001'),
    c("A1-28", "AG001", "aggregated-earlier", 'small = df.groupBy("k").count()\nrows = small.collect()  # expect: AG001'),
    c("A1-29", "AG001", "bound-negative", "rows = df.limit(10).collect()"),
    c("A1-30", "AG001", "bound-negative", "rows = df.head(5)"),
    c("A1-31", "AG001", "bound-negative", "rows = df.take(5)"),
    c("A1-32", "AG001", "bound-negative", "row = df.first()"),
    c("A1-33", "AG001", "bound-negative", "pdf = df.sample(0.1).toPandas()"),
    c("A1-34", "AG001", "bound-negative", "pdf = df.limit(5).toPandas()"),
    c("A1-35", "AG001", "bound-negative", 'pdf = df.where(df.a > 1).limit(100).orderBy("a").toPandas()'),
    c("A1-36", "AG001", "bound-negative", "rows = df.sample(False, 0.01).collect()"),
    c("A1-37", "AG001", "bound-negative", "frame = lf.head(100).collect()"),
    c("A1-38", "AG001", "bound-earlier-statement", "small = df.limit(5)\nrows = small.collect()", hard="a bound on an earlier statement is not tracked (documented limitation)"),
    c("A1-39", "AG001", "bound-earlier-statement", "head = lf.head(50)\nframe = head.collect()", hard="a bound on an earlier statement is not tracked (documented limitation)"),
    c("A1-40", "AG001", "not-a-dataframe", "import gc\ngc.collect()", hard="receiver type is unknown, so the garbage collector's collect() is flagged"),
    c("A1-41", "AG001", "not-a-dataframe", "stats = counter.collect()", hard="receiver type is unknown (a custom class with a collect method)"),
    c("A1-42", "AG001", "suppressed", "rows = df.collect()  # ast-guard: ignore[AG001]"),
    c("A1-43", "AG001", "suppressed-other-rule", "rows = df.collect()  # ast-guard: ignore[AG003]  # expect: AG001"),
    c("A1-44", "AG001", "aliased-method", "m = df.collect\nrows = m()  # expect: AG001", hard="a method stored in a variable is invisible to a name-based rule"),
    c("A1-45", "AG001", "getattr", 'rows = getattr(df, "collect")()  # expect: AG001', hard="dynamic attribute access is invisible to a name-based rule"),
    c("A1-46", "AG001", "arrow-table", "pdf = table.to_pandas()", unclear=True),
    c("A1-47", "AG001", "decorated", "@task\ndef load(df):\n    return df.toPandas()  # expect: AG001"),
    c("A1-48", "AG001", "nested-call", "save(df.select('a').collect())  # expect: AG001"),
    c("A1-49", "AG001", "assignment-expression", "if (rows := df.collect()):  # expect: AG001\n    pass"),
    c("A1-50", "AG001", "bound-and-collect-separate", "df.limit(5).show()\nrows = df.collect()  # expect: AG001"),
    # ---------------------------------------------------------------- AG002: cross join / keyless join
    c("A2-01", "AG002", "crossJoin", "out = a.crossJoin(b)  # expect: AG002"),
    c("A2-02", "AG002", "keyless", "out = a.join(b)  # expect: AG002"),
    c("A2-03", "AG002", "how-cross", 'out = a.join(b, how="cross")  # expect: AG002'),
    c("A2-04", "AG002", "how-only", 'out = a.join(b, how="left")  # expect: AG002'),
    c("A2-05", "AG002", "how-only", 'out = a.join(b, how="inner")  # expect: AG002'),
    c("A2-06", "AG002", "other-keyword", "out = a.join(other=b)  # expect: AG002"),
    c("A2-07", "AG002", "multiline-chain", 'out = (  # expect: AG002\n    a.select("x")\n    .join(b)\n    .where(c)\n)'),
    c("A2-08", "AG002", "crossJoin-in-chain", 'out = a.alias("l").crossJoin(a.alias("r"))  # expect: AG002'),
    c("A2-09", "AG002", "crossJoin-via-class", "out = DataFrame.crossJoin(a, b)  # expect: AG002"),
    c("A2-10", "AG002", "pandas-index-join", "out = a.join(b)  # expect: AG002"),
    c("A2-11", "AG002", "pandas-suffix-only", 'out = a.join(b, lsuffix="_l")  # expect: AG002'),
    c("A2-12", "AG002", "in-function", "def f(a, b):\n    return a.join(b)  # expect: AG002"),
    c("A2-13", "AG002", "keyed-positional", 'out = a.join(b, "id")'),
    c("A2-14", "AG002", "keyed-condition", "out = a.join(b, a.id == b.id)"),
    c("A2-15", "AG002", "keyed-on", 'out = a.join(b, on="id")'),
    c("A2-16", "AG002", "keyed-list", 'out = a.join(b, ["id", "day"], "left")'),
    c("A2-17", "AG002", "keyed-on-list", 'out = a.join(b, on=["id"], how="left")'),
    c("A2-18", "AG002", "keyed-left-right", 'out = a.join(b, left_on="x", right_on="y")'),
    c("A2-19", "AG002", "keyed-using", 'out = a.join(b, using="id")'),
    c("A2-20", "AG002", "keyed-pandas", 'out = a.join(b, on="k")'),
    c("A2-21", "AG002", "string-join", 'text = ", ".join(names)'),
    c("A2-22", "AG002", "string-join", 'text = "".join(chunk for chunk in parts)'),
    c("A2-23", "AG002", "string-join-list-arg", 'text = sep.join([a, b])'),
    c("A2-24", "AG002", "path-join", "p = os.path.join(base, name)"),
    c("A2-25", "AG002", "path-join", 'p = os.path.join("data")'),
    c("A2-26", "AG002", "fstring-join", 'text = f"{x}".join(items)'),
    c("A2-27", "AG002", "string-join-variable-receiver", "text = sep.join(parts)", hard="a variable receiver with a variable argument looks like a DataFrame join (documented)"),
    c("A2-28", "AG002", "string-join-call-arg", "text = sep.join(map(str, xs))", hard="a call argument is not recognised as a non-DataFrame argument"),
    c("A2-29", "AG002", "thread-join", "worker.join()", hard="zero-argument join (a thread or process) is treated as a keyless DataFrame join"),
    c("A2-30", "AG002", "thread-join-timeout", "worker.join(timeout=5)", hard="a thread join with a timeout keyword is treated as a keyless join"),
    c("A2-31", "AG002", "queue-join", "jobs.join()", hard="zero-argument join (a queue) is treated as a keyless DataFrame join"),
    c("A2-32", "AG002", "suppressed", "out = a.join(b)  # ast-guard: ignore[AG002]"),
    c("A2-33", "AG002", "suppressed-other-rule", "out = a.join(b)  # ast-guard: ignore[AG001]  # expect: AG002"),
    c("A2-34", "AG002", "on-none", "out = a.join(b, on=None)  # expect: AG002", hard="an explicit on=None is counted as having a key"),
    c("A2-35", "AG002", "on-empty-list", "out = a.join(b, on=[])  # expect: AG002", hard="an empty key list is counted as having keys"),
    c("A2-36", "AG002", "pandas-cross-merge", 'out = a.merge(b, how="cross")  # expect: AG002', hard="only join/crossJoin are inspected, not merge"),
    c("A2-37", "AG002", "merge-negative", 'out = a.merge(b, on="id")'),
    c("A2-38", "AG002", "aliased-method", "j = a.join\nout = j(b)  # expect: AG002", hard="a method stored in a variable is invisible to a name-based rule"),
    c("A2-39", "AG002", "boolean-literal-condition", "out = a.join(b, F.lit(True))", unclear=True),
    c("A2-40", "AG002", "join-in-comprehension", "outs = [a.join(x) for x in tables]  # expect: AG002"),
    # ---------------------------------------------------------------- AG003: hard-coded paths
    c("A3-01", "AG003", "absolute-posix", 'df = spark.read.csv("/data/in.csv")  # expect: AG003'),
    c("A3-02", "AG003", "absolute-posix-dir", 'base = "/mnt/raw/events/"  # expect: AG003'),
    c("A3-03", "AG003", "s3", 'df = spark.read.parquet("s3://bucket/key")  # expect: AG003'),
    c("A3-04", "AG003", "s3a", 'df = spark.read.parquet("s3a://bucket/key")  # expect: AG003'),
    c("A3-05", "AG003", "gs", 'df = spark.read.parquet("gs://bucket/key")  # expect: AG003'),
    c("A3-06", "AG003", "abfss", 'df = spark.read.parquet("abfss://c@acct.dfs.core.windows.net/x")  # expect: AG003'),
    c("A3-07", "AG003", "hdfs", 'df = spark.read.parquet("hdfs://nn/x")  # expect: AG003'),
    c("A3-08", "AG003", "dbfs", 'df = spark.read.parquet("dbfs:/mnt/x")  # expect: AG003'),
    c("A3-09", "AG003", "file-uri", 'df = spark.read.parquet("file:///tmp/x")  # expect: AG003'),
    c("A3-10", "AG003", "windows-backslash", 'df = pd.read_csv("C:\\\\data\\\\x.csv")  # expect: AG003'),
    c("A3-11", "AG003", "windows-slash", 'df = pd.read_csv("D:/data/x.csv")  # expect: AG003'),
    c("A3-12", "AG003", "keyword-argument", 'df = spark.read.load(path="/data/x")  # expect: AG003'),
    c("A3-13", "AG003", "module-constant", 'INPUT = "/data/in"  # expect: AG003'),
    c("A3-14", "AG003", "default-argument", 'def run(path="/data/in"):  # expect: AG003\n    return path'),
    c("A3-15", "AG003", "fstring-prefix", 'p = f"/data/{day}/x.csv"  # expect: AG003'),
    c("A3-16", "AG003", "dev-null", 'sink = open("/dev/null", "w")  # expect: AG003'),
    c("A3-17", "AG003", "in-list", 'paths = ["/data/a", "/data/b"]  # expect: AG003, AG003'),
    c("A3-18", "AG003", "relative", 'df = pd.read_csv("data/in.csv")'),
    c("A3-19", "AG003", "dot-relative", 'df = pd.read_csv("./data/in.csv")'),
    c("A3-20", "AG003", "parent-relative", 'df = pd.read_csv("../data/in.csv")'),
    c("A3-21", "AG003", "environment", 'path = os.environ["INPUT_PATH"]'),
    c("A3-22", "AG003", "path-object", 'p = Path(__file__).parent / "in.csv"'),
    c("A3-23", "AG003", "http-url", 'u = "http://example.com/data/x.csv"'),
    c("A3-24", "AG003", "https-url", 'u = "https://example.com/data/x.csv"'),
    c("A3-25", "AG003", "single-segment", 'p = "/tmp"'),
    c("A3-26", "AG003", "slash-only", 'sep = "/"'),
    c("A3-27", "AG003", "environment-default", 'path = os.environ.get("IN", "/data/in")  # expect: AG003'),
    c("A3-28", "AG003", "suppressed", 'p = "/data/in"  # ast-guard: ignore[AG003]'),
    c("A3-29", "AG003", "suppressed-other-rule", 'p = "/data/in"  # ast-guard: ignore[AG001]  # expect: AG003'),
    c("A3-30", "AG003", "regex-not-a-path", 'pat = re.compile(r"^/api/v1/items")', hard="a regular expression that looks like a path is flagged"),
    c("A3-31", "AG003", "docstring-mention", 'def f():\n    """Reads /data/in.csv and writes /data/out.csv."""\n    return 1', hard="a path mentioned in a docstring is flagged"),
    c("A3-32", "AG003", "log-message", 'log.info("reading /data/in/part-0")', hard="a path inside a log message is flagged"),
    c("A3-33", "AG003", "unc-path", 'p = "\\\\\\\\server\\\\share\\\\x.csv"  # expect: AG003', hard="UNC paths are not in the pattern"),
    c("A3-34", "AG003", "home-relative", 'p = "~/data/in.csv"', unclear=True),
    c("A3-35", "AG003", "mixed-case-scheme", 'p = "S3://bucket/key"  # expect: AG003', hard="URI scheme matching is case sensitive"),
    # ---------------------------------------------------------------- AG000: unparseable files
    c("A0-01", "AG000", "unclosed-paren", "x = (1 +\n"),
    c("A0-02", "AG000", "python2-print", 'print "hello"\n'),
    c("A0-03", "AG000", "bad-indent", "def f():\nreturn 1\n"),
    c("A0-04", "AG000", "null-byte", "x = 1\x00\n"),
    c("A0-05", "AG000", "parses-empty", ""),
    c("A0-06", "AG000", "parses-comment-only", "# nothing here\n"),
    c("A0-07", "AG000", "parses-modern-syntax", "match x:\n    case 1:\n        y = 2\n"),
    c("A0-08", "AG000", "unterminated-string", 'x = "abc\n'),
]
