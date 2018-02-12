import requests, json
from shutil import copyfile
from yattag import Doc, indent

copyfile("./helper.js", "/var/www/html/helper.js")


def getFailures(url) :
	testNames = []
	testErrs = []
	testresult = requests.get(url,auth=(user, password))
	testresult = json.loads(testresult.text,strict=False)
	for test in testresult['suites'] :
		for case in test['cases'] :
			if case['status'] != 'PASSED' and case['status'] != 'SKIPPED' and case['status'] != 'FIXED':
				testNames.append(case['name']+":"+case['className'])
				if case['errorDetails'] :
					testErrs.append(case['errorDetails'][:400])
				else :
					testErrs.append(case['errorStackTrace'][:400])
					
	return testNames, testErrs
	
doc, tag, text = Doc().tagtext()
user="admin"
password="admin"

jobs = []
summary = {'ppc' : [], 'x86' : []}
xserver_url="http://10.53.17.125:7070"
pserver_url="http://10.88.67.131:7070"
job_url="/job/"
a_j="/api/json"
req=xserver_url+a_j
resp = requests.get(req,auth=(user, password))

for job in resp.json()['jobs'] :
	 jobs.append(job['name'])



data = {}
with tag('html'):
	with tag('head'):
		with tag('style'):
			text('table, th, td { border: 1px solid black; vertical-align:top; padding: 3px} table {table-layout:fixed} td {word-wrap:break-word} th{background-color: DodgerBlue; color: white;}')

		with tag('script', src='helper.js') :
			text('function hideAll(){console.log("hideAll")}function showme(clicked){console.log("showme");var idVal=clicked.substring(7);var all=document.getElementsByName("data");var i;for(i=0;i<all.length;i++){all[i].style.display="none"}var allSum=document.getElementsByName("summary");for(i=0;i<allSum.length;i++){allSum[i].style.display="none"}document.getElementById(idVal).style.display="block"}')

	with tag('body', onload="hideAll();"):
		with tag('div',style="display: table-cell; width: 140px"):
			for key in summary:
				with tag('div'):
					with tag('a', href='#', id='anchor_'+key, onclick="showme(this.id);"):
						text(key.upper()+' SUMMARY')
			with tag('div'):
				text('=============')
				
			for job in jobs :
				if job == "ALL" or job == "hadooppipe" or job == "lucidworks-solr" :
					continue
				with tag('div'):
					#job_display_name = str(job).upper().replace('PIPE','')
					with tag('a', href='#', id='anchor_'+job, onclick="showme(this.id);"):
						j = str(job)
						j = j.upper().replace('PIPE','')
						j = j.upper().replace('-MASTER','')
						text(j)
			
		with tag('div',style="display: table-cell"):
			for job in jobs :
				ppcsummary_detail = {}
				x86summary_detail = {}
				#cheat to exclude
				if job == "ALL" or job == "hadooppipe" or job == "lucidworks-solr" :
					continue
				job_display_name = str(job).upper().replace('PIPE','')
				job_display_name = job_display_name.replace('-MASTER','')
				
				print "Procesing Job : " + job
							
				ppc_job = pserver_url + job_url + job + a_j
				x86_job = xserver_url + job_url + job + a_j
				ppc_resp = requests.get(ppc_job,auth=(user, password)).json()
				x86_resp = requests.get(x86_job,auth=(user, password)).json()
				if 'lastCompletedBuild' not in ppc_resp.keys() or not ppc_resp['lastCompletedBuild']:
					continue
				if 'lastCompletedBuild' not in x86_resp.keys() or not x86_resp['lastCompletedBuild']:
					continue
				
				ppc_last_builds = ppc_resp['builds']
				x86_last_builds = x86_resp['builds']
				
				ppc_lastBuild = requests.get(ppc_resp['lastCompletedBuild']['url']+a_j,auth=(user, password)).json()
				x86_lastBuild = requests.get(x86_resp['lastCompletedBuild']['url']+a_j,auth=(user, password)).json()
				
				ppcsummary_detail['name'] = job_display_name
				ppcsummary_detail['job'] = job
				ppcsummary_detail['result'] = ppc_lastBuild['result']
				x86summary_detail['name'] = job_display_name
				x86summary_detail['job'] = job
				x86summary_detail['result'] = x86_lastBuild['result']
				
				with tag('div', id=job, name='data', style="display:none") :
					with tag('h2') :
						with tag('center') :
							text(job_display_name)
					with tag('table',width="100%",border="1",cellspacing="0",cellpadding="0"):
						with tag('tbody'):
							#header
							with tag('tr'):
								with tag('th',width='10%'):
									text('')
								with tag('th'):
									text('PPC')
								with tag('th'):
									text('x86')
							#summary
							with tag('tr'):
								with tag('td'):
									text('Summary')
								with tag('td'):
									revHash, revName = "", ""
									for action in ppc_lastBuild['actions'] :
										if action and action['_class'] == "hudson.tasks.junit.TestResultAction" :
											with tag('div') :
												text('Total Count : {0}'.format(action['totalCount']))
											with tag('div') :
												text('Failed Count : {0}'.format(action['failCount']))
											with tag('div') :
												text('Skipped Count : {0}'.format(action['skipCount']))
										if action and action['_class'] == "hudson.plugins.git.util.BuildData" :
											revHash = action['lastBuiltRevision']['branch'][0]['SHA1']
											revName = action['lastBuiltRevision']['branch'][0]['name']
									d = ""
									ms = ppc_lastBuild['duration']
									min=(ms/(1000*60))%60
									hr=(ms/(1000*60*60))%24
									if hr >= 1 :
										d= str(hr) +" hr " + str(min) + " min"
									else :
										d= str(min) + " min"
									with tag('div') :
										text('Duration : {0}'.format(d))
									with tag('div') :
										text('Branch Details: {0}'.format(revName))
									with tag('div') :
										text('Last Revision: {0}'.format(revHash))
								with tag('td'):
									revHash, revName = "", ""
									for action in x86_lastBuild['actions'] :
										if action and action['_class'] == "hudson.tasks.junit.TestResultAction" :
											with tag('div') :
												text('Total Count : {0}'.format(action['totalCount']))
											with tag('div') :
												text('Failed Count : {0}'.format(action['failCount']))
											with tag('div') :
												text('Skipped Count : {0}'.format(action['skipCount']))
										if action and action['_class'] == "hudson.plugins.git.util.BuildData" :
											revHash = action['lastBuiltRevision']['branch'][0]['SHA1']
											revName = action['lastBuiltRevision']['branch'][0]['name']

									d = ""
									ms = x86_lastBuild['duration']
									min=(ms/(1000*60))%60
									hr=(ms/(1000*60*60))%24
									if hr >= 1 :
										d= str(hr) +" hr " + str(min) + " min"
									else :
										d= str(min) + " min"
									with tag('div') :
										text('Duration : {0}'.format(d))
									with tag('div') :
										text('Branch Details: {0}'.format(revName))
									with tag('div') :
										text('Last Revision: {0}'.format(revHash))
							#Status
							with tag('tr'):
								with tag('td'):
									text('Result')
								with tag('td'):
									text(ppc_lastBuild['result'])
								with tag('td'):				
									text(x86_lastBuild['result'])
							#Failures
							ppc_tests, ppc_testErrs, x86_tests, x86_testErrs = [], [], [], []
							if ppc_lastBuild['result'] != 'FAILURE' and ppc_lastBuild['result'] != 'ABORTED':
								ppc_tests, ppc_testErrs = getFailures(ppc_resp['lastCompletedBuild']['url']+'testReport'+a_j)
								
							if x86_lastBuild['result'] != 'FAILURE' and x86_lastBuild['result'] != 'ABORTED':
								x86_tests, x86_testErrs = getFailures(x86_resp['lastCompletedBuild']['url']+'testReport'+a_j)

							ppcsummary_detail['failed'] = len(ppc_tests)
							x86summary_detail['failed'] = len(x86_tests)
							
							with tag('tr'):
								with tag('td'):
									text('Failures')
								with tag('td'):
									with tag('ol'):
										for t in ppc_tests :
											with tag('li'):
												with tag('div'):
													text(t)
								with tag('td') :
									with tag('ol'):
										for t in x86_tests :
											with tag('div'):
												with tag('li'):
													text(t)
							#Description
							with tag('tr'):
								with tag('td'):
									text('Description')
								with tag('td'):
									with tag('ol'):
										for t in ppc_testErrs :
											with tag('div'):
												with tag('li'):
													text(t)
								with tag('td'):				
									with tag('ol'):
										for t in x86_testErrs :
											with tag('div'):
												with tag('li'):
													text(t)
							#Unique Failures
							with tag('tr'):
								with tag('td'):
									text('Unique Failures')
								with tag('td'):
									result = [x for x in ppc_tests if x not in x86_tests]
									ppcsummary_detail['unique'] = len(result)
									with tag('ol'):
										for t in result :
											with tag('li'):
												with tag('div'):
													text(t)
								with tag('td'):
									result = [x for x in x86_tests if x not in ppc_tests]
									x86summary_detail['unique'] = len(result)
									with tag('ol'):
										for t in result :
											with tag('li'):
												with tag('div'):
													text(t)
							
							#Last 5 builds status
							with tag('tr'):
								with tag('td'):
									text('Last 5 Builds')
								with tag('td'):
									i = 0
									for build in ppc_last_builds :
										if (i < 5) :
											try  :
												builds_resp = requests.get(build['url']+a_j+"",auth=(user, password))
												with tag('div') :
													text(builds_resp.json()['result'])
											except :
												continue
											
										i = i + 1
								with tag('td'):
									i = 0
									for build in x86_last_builds :
										if (i < 5) :
											try  :
												builds_resp = requests.get(build['url']+a_j+"",auth=(user, password))
												with tag('div') :
													text(builds_resp.json()['result'])
											except :
												continue
											
										i = i + 1
				summary['ppc'].append(ppcsummary_detail)
				summary['x86'].append(x86summary_detail)
			
			for key in summary :
				if key == 'ppc' :
					disp = 'block'
				else :
					disp = 'none'
				with tag('div', id=key, name='summary', style="display:"+disp) :
					with tag('h2') :
						with tag('center') :
							text(key.upper()+' SUMMARY')
					with tag('table',width="100%",border="1",cellspacing="0",cellpadding="0"):
						with tag('tbody'):
							#header
							with tag('tr'):
								with tag('th'):
									text('Package Name')
								with tag('th'):
									text('Result')
								with tag('th'):
									text('Failed Count')
								with tag('th'):
									text('Unique Count')
							for summary_detail in summary[key]:
								with tag('tr'):
									with tag('td'):
										with tag('a', href='#', id='anchor_'+summary_detail['job'], onclick="showme(this.id);"):
											text(summary_detail['name'])
									with tag('td'):
										text(summary_detail['result'])
									with tag('td'):
										text(summary_detail['failed'])
									with tag('td'):
										text(summary_detail['unique'])
					
result = doc.getvalue()
print "Writing result to a file at /var/www/html/test.html"
with open('/var/www/html/test.html','w') as afile :
	afile.write(result.encode('utf-8'))
