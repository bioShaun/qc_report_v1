
# coding:UTF-8
'''
this is py2report's pdf_report moudle which a python script generate pdf mRNA report
this version only run on 34
log:
create by chencheng on 2017-06-13
add all href and plot_size on 2017-06-14
add all function doc on 2017-06-16
'''
import os
import sys
import subprocess
from . import mRNA_data_dict, pdf_analysis_path, pdf_jinja_env, pdf_settings, pdf_plots_size_dict, company_setting_mannager

reload(sys)
sys.setdefaultencoding('utf-8')

PROJECT_CN = {
    'rna': '转录组测序',
    'lnc': '长链非编码 RNA 测序',
    'reseq': '全基因组重测序',
    'exome': '外显子组测序',
    'denovo': '基因组测序',
    'chip': 'ChIP-Seq 测序',
}


main_path = os.path.dirname(os.path.realpath(__file__))
ref_file_path = os.path.join(main_path, 'pdf_templates', 'ref.bib')


def cut_overlong_table(row_list, max_len=int(pdf_settings['max_cell_len'])):
    '''
    param:
    row_list: each analysis part's table rwo list apply in three_line_list function
    max_cell_len: threshold value to cut table cell
    function: cut table cell's length when over 20 chars
    '''
    for i in range(len(row_list)):
        if len(row_list[i]) > max_len:
            row_list[i] = row_list[i][:max_len] + '...'
    return row_list


def three_line_list(input_path, colunms, split='\t'):
    '''
    param:
    input_path: each analysis part's table path
    colunms: threshold value to table colunms
    function: transform each analysis part's table into table_list
    '''
    if input_path:
        with open(input_path, 'r+') as f:
            data = f.readlines()
            thead = data[0]
            table_cols = len(thead.strip().split(split))
            tbody = data[1:]

            if table_cols < colunms:
                cols = table_cols
            else:
                cols = colunms

            table_list = []
            table_begin = '\\begin{longtable}{%s}' % ('c' * cols)
            table_list.append(table_begin)

            if cols > 3:
                head_list = cut_overlong_table(
                    thead.strip('\n').split(split))[:cols]
            else:
                head_list = thead.strip('\n').split(split)

            head_str = '&'.join(head_list).replace('_', '\_').replace(
                '%', '\%').replace('#', '\#') + r'\\'
            table_list.append(head_str)
            for line in tbody:
                if cols > 3:
                    each_list = cut_overlong_table(
                        line.strip('\n').split(split))[:cols]
                else:
                    each_list = line.strip('\n').split(split)
                each_str = '&'.join(each_list).replace('_', '\_').replace(
                    '%', '\%').replace('#', '\#') + r'\\'
                table_list.append(each_str)
            return table_list
    else:
        return None


def check_file(file_dict, generate_report_path, part):
    '''
    param:
    file_dict:each analysis part's path dict
    generate_report_path:a path where to your analysis's report data
    function:check each path's exists and add generate_report_path into them
    '''
    flag = 1
    for key, value in file_dict.items():
        file_dict[key] = os.path.join(generate_report_path, value)
        if not os.path.exists(file_dict[key]):
            flag = 0
            print(file_dict[key])
            if part:
                print '{file} is not find in: {file_path}'.format(file=key, file_path=os.path.dirname(file_dict[key]))
                sys.exit(1)
            else:
                file_dict[key] = None
    return flag


def run_tex(tex_path):
    '''
    param:
    tex_path:generate pdf report's tex path
    function:transform tex file into pdf file
    '''
    tex_dir = os.path.dirname(tex_path)
    tex_file = os.path.basename(tex_path)
    os.chdir(tex_dir)
    aux_file = tex_file.replace('tex', 'aux')
    rm_set = ['.aux', '.log', '.out', '.toc',
              '.tmp', '.bib', '.bbl', '.blg', '.tex']
    subprocess.call('cp {ref_file} {tex_dir}'.format(
        ref_file=ref_file_path, tex_dir=tex_dir), shell=True)
    subprocess.call('xelatex {tex_file} > summary'.format(
        tex_file=tex_file), shell=True)
    subprocess.call('bibtex {aux_file}'.format(aux_file=aux_file), shell=True)
    subprocess.call('xelatex {tex_file} > summary'.format(
        tex_file=tex_file), shell=True)
    subprocess.call('xelatex {tex_file} > summary'.format(
        tex_file=tex_file), shell=True)
    # for each_file in os.listdir(tex_dir):
    #     if os.path.splitext(each_file)[1] in rm_set:
    #         subprocess.call('rm {file}'.format(
    #             file=os.path.join(tex_dir, each_file)), shell=True)

    print '---------------------'
    print 'pdf mRNA report done!'
    print '---------------------'


def enrichment_analysis_part(generate_report_path, part):
    enrichment_analysis_path = pdf_analysis_path['enrichment']
    if check_file(enrichment_analysis_path, generate_report_path, part):
        go_list = three_line_list(
            enrichment_analysis_path['go_table_path'], colunms=7)

        if enrichment_analysis_path['dag_bp_path'] and enrichment_analysis_path['dag_cc_path'] and enrichment_analysis_path['dag_mf_path']:
            dag_plots = True
        else:
            dag_plots = False

        enrichment_dict = dict(enrichment='enrichment',
                               go_table_path=enrichment_analysis_path,
                               go_begin=go_list[0],
                               go_head=go_list[1],
                               go_body=go_list[2:15],
                               # go_barplot_path=enrichment_analysis_path['go_barplot_path'],
                               dag_plots=dag_plots,
                               dag_bp_path=enrichment_analysis_path['dag_bp_path'],
                               dag_cc_path=enrichment_analysis_path['dag_cc_path'],
                               dag_mf_path=enrichment_analysis_path['dag_mf_path'])
    else:
        enrichment_dict = {}
    return enrichment_dict


def fastqc_analysis_part(generate_report_path, part):
    fastqc_analysis_path = pdf_analysis_path['fastqc']
    check_file(fastqc_analysis_path, generate_report_path, part)
    qc_list = three_line_list(fastqc_analysis_path['qc_table_path'], colunms=6)

    fastqc_dict = dict(
        qc_begin=qc_list[0], qc_head=qc_list[1], qc_body=qc_list[2:],
        gc_barplot_path=fastqc_analysis_path['gc_barplot_path'],
        reads_quality_path=fastqc_analysis_path['reads_quality_path'],
        qc_table_path=fastqc_analysis_path['qc_table_path'],
        data_stat='data_stat')

    snp_path = pdf_analysis_path['snp']
    if check_file(snp_path, generate_report_path, part=False):
        snp_list = three_line_list(snp_path['snp_num_table'],
                                   colunms=4)
        fastqc_dict.update(dict(
            snp='snp',
            snp_num_begin=snp_list[0],
            snp_num_head=snp_list[1],
            snp_num_body=snp_list[2:],
            snp_num_table=snp_path['snp_num_table'],
            snp_plot_path=snp_path['snp_plot_path'],
        ))

    return fastqc_dict


def mapping_analysis_part(generate_report_path, part):
    mapping_analysis_path = pdf_analysis_path['mapping']
    if check_file(mapping_analysis_path, generate_report_path, part):
        mapping_list = three_line_list(mapping_analysis_path['mapping_table_path'],
                                       colunms=4)

        mapping_dict = dict(
            mapping_begin=mapping_list[0],
            mapping_head=mapping_list[1],
            mapping_body=mapping_list[2:],
            mapping_plot_path=mapping_analysis_path['mapping_plot_path'],
            mapping_table_path=mapping_analysis_path['mapping_table_path'],
            mapping='mapping')
    else:
        mapping_dict = {}
    return mapping_dict


def lnc_analysis_part(generate_report_path, part):
    lnc_analysis_path = pdf_analysis_path['lnc']
    if check_file(lnc_analysis_path, generate_report_path, part):
        lnc_dict = dict(
            lnc_pie_plot=lnc_analysis_path['lnc_pie_plot'],
            feelnc_plot=lnc_analysis_path['feelnc_plot'],
            lnc_filter='lnc_filter')
    else:
        lnc_dict = {}
    return lnc_dict


def rseqc_analysis_part(generate_report_path, part):
    rseqc_analysis_path = pdf_analysis_path['rseqc']
    if os.path.exists(os.path.join(generate_report_path, mRNA_data_dict['rseqc'])):
        check_file(rseqc_analysis_path, generate_report_path, part)
        rseqc_dict = dict(data_control='data_control',
                          genebody_coverage_plot_path=rseqc_analysis_path['genebody_coverage_plot_path'],
                          inner_distance_plot_path=rseqc_analysis_path['inner_distance_plot_path'],
                          read_distribution_plot_path=rseqc_analysis_path['read_distribution_plot_path'],
                          )

    return rseqc_dict


def quant_analysis_part(generate_report_path, part):
    diff_analysis_path = pdf_analysis_path['diff']
    quantification_analysis_path = pdf_analysis_path['quantification']
    check_file(diff_analysis_path, generate_report_path, part)
    check_file(quantification_analysis_path, generate_report_path, part)
    quant_dict = dict(
        gene_expression_path=quantification_analysis_path['gene_expression_path'],
        pca_plot_path=quantification_analysis_path['pca_plot_path'],
        volcano_plot_path=diff_analysis_path['volcano_plot_path'],
        quant='quant',
        diff='diff')

    return quant_dict


def check_analysis_part(
        generate_report_path, analysis_part,
        part_dict, label, part, func):
    if os.path.exists(os.path.join(generate_report_path, analysis_part)):
        analysis_dict = func(generate_report_path, part)
    else:
        analysis_dict = part_dict
        print '---{analysis_module} analysis part missing---'.format(analysis_module=label)

    return analysis_dict
    # pdf_param_dict.update(analysis_dict)


def create_pdf_report(generate_report_path, project_name,
                      project_id, part, company, project_type):
    '''
    param:a path where to your analysis's report data
    function:generate report tex file
    '''
    pdf_param_dict = {}
    pdf_param_dict.update(pdf_plots_size_dict)
    pdf_head_dict = dict(project_name=project_name,
                         project_id=project_id,
                         address=pdf_settings['address'],
                         phone=pdf_settings['phone'],
                         pipeline_path=pdf_settings['pipeline_path'],
                         mRNAworkflow_path=pdf_settings['mRNAworkflow_path']
                         )
    pdf_param_dict.update(pdf_head_dict)
    pdf_head_sup_dict = dict(
        logo_path=company_setting_mannager[company]['logo_path'],
        company_full_name=company_setting_mannager[company]['company_full_name'],
        company_website=company_setting_mannager[company]['company_website'],
        company_abbr=company_setting_mannager[company]['company_abbr'],
        cover_path=company_setting_mannager[company]['cover_path'],
    )
    pdf_param_dict.update(pdf_head_sup_dict)
    # enrichment:
    # fastqc:
    fastqc_dict = check_analysis_part(generate_report_path,
                                      mRNA_data_dict['fastqc'],
                                      {'data_stat': None},
                                      'fastqc', part,
                                      func=fastqc_analysis_part)
    mapping_dict = check_analysis_part(generate_report_path,
                                       mRNA_data_dict['mapping'],
                                       {'mapping': None},
                                       'mapping', part,
                                       func=mapping_analysis_part)
    enrich_dict = check_analysis_part(generate_report_path,
                                      mRNA_data_dict['enrichment'],
                                      {'enrichment': None},
                                      'enrichment', part,
                                      func=enrichment_analysis_part)
    quant_dict = check_analysis_part(generate_report_path,
                                     mRNA_data_dict['quantification'],
                                     {'quant': None, 'diff': None},
                                     'quant', part,
                                     func=quant_analysis_part)
    lnc_dict = check_analysis_part(generate_report_path,
                                   mRNA_data_dict['lnc'],
                                   {'lnc_filter': None},
                                   'lnc', part,
                                   func=lnc_analysis_part)

    pdf_param_dict.update(fastqc_dict)
    pdf_param_dict.update(mapping_dict)
    pdf_param_dict.update(enrich_dict)
    pdf_param_dict.update(quant_dict)
    pdf_param_dict.update(lnc_dict)

    report_name = PROJECT_CN.get(project_type)
    pdf_param_dict.update({
        'report_name': report_name,
    })

    template = pdf_jinja_env.get_template('mRNA_base')

    if not os.path.exists(generate_report_path):
        os.makedirs(generate_report_path)
    with open(os.path.join(generate_report_path,
                           '{pn}.tex'.format(pn=project_id)), 'w+') as f:
        f.write(template.render(pdf_param_dict))
    print '-------------------------'
    print 'pdf report tex file done!'
    print '-------------------------'
    run_tex(tex_path=os.path.join(generate_report_path,
                                  '{pn}.tex'.format(pn=project_id)))
