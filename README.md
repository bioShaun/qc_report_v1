# fastqcReport
fastqcReport 是一个以 Python 模板语言 [**jinja2**](http://jinja.pocoo.org/docs/2.9/) 作为模板引擎,根据fastQC结果文件自动生成 pdf 报告的 python 包。

## 参数
- option: -n(--name) 报告名称

```
qc_report your_report_result_path -n your_report_name
```

## 安装

```bash

git clone https://github.com/bioShaun/qc_report_v1.git
cd qc_report_v1
python setup.py install

```

