Search.setIndex({docnames:["devices","exceptions","gui","index","monitors","names","network","parse","scanner","symbol_types"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":5,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["devices.rst","exceptions.rst","gui.rst","index.rst","monitors.rst","names.rst","network.rst","parse.rst","scanner.rst","symbol_types.rst"],objects:{"":[[0,0,0,"-","devices"],[1,0,0,"-","exceptions"],[4,0,0,"-","monitors"],[5,0,0,"-","names"],[6,0,0,"-","network"],[7,0,0,"-","parse"],[8,0,0,"-","scanner"],[9,0,0,"-","symbol_types"]],"devices.Devices":[[0,2,1,"","add_device"],[0,2,1,"","add_input"],[0,2,1,"","add_output"],[0,2,1,"","cold_startup"],[0,2,1,"","find_devices"],[0,2,1,"","get_device"],[0,2,1,"","get_signal_ids"],[0,2,1,"","get_signal_name"],[0,2,1,"","make_clock"],[0,2,1,"","make_d_type"],[0,2,1,"","make_device"],[0,2,1,"","make_gate"],[0,2,1,"","make_switch"],[0,2,1,"","set_switch"]],"exceptions.Errors":[[1,2,1,"","add_error"],[1,2,1,"","print_error_messages"]],"exceptions.ParseBaseException":[[1,2,1,"","explain"],[1,3,1,"","message"]],"exceptions.SemanticErrors":[[1,1,1,"","ConnectInToIn"],[1,1,1,"","ConnectOutToOut"],[1,1,1,"","FloatingInput"],[1,1,1,"","InvalidAndParam"],[1,1,1,"","InvalidClockParam"],[1,1,1,"","MonitorInputPin"],[1,1,1,"","MonitorSamePin"],[1,1,1,"","MultipleConnections"],[1,1,1,"","NameClash"],[1,1,1,"","UndefinedDevice"],[1,1,1,"","UndefinedInPin"],[1,1,1,"","UndefinedOutPin"]],"exceptions.SemanticErrors.ConnectInToIn":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.ConnectOutToOut":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.FloatingInput":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.InvalidAndParam":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.InvalidClockParam":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.MonitorInputPin":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.MonitorSamePin":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.MultipleConnections":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.NameClash":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.UndefinedDevice":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.UndefinedInPin":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SemanticErrors.UndefinedOutPin":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors":[[1,1,1,"","InvalidSwitchParam"],[1,1,1,"","MissingParam"],[1,1,1,"","MissingSemicolon"],[1,1,1,"","NoConnections"],[1,1,1,"","NoDevices"],[1,1,1,"","NoMonitors"],[1,1,1,"","UnexpectedEOF"],[1,1,1,"","UnexpectedParam"],[1,1,1,"","UnexpectedToken"]],"exceptions.SyntaxErrors.InvalidSwitchParam":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.MissingParam":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.MissingSemicolon":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.NoConnections":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.NoDevices":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.NoMonitors":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.UnexpectedEOF":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.UnexpectedParam":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"exceptions.SyntaxErrors.UnexpectedToken":[[1,3,1,"","message"],[1,3,1,"","symbol"]],"monitors.Monitors":[[4,2,1,"","display_signals"],[4,2,1,"","get_margin"],[4,2,1,"","get_monitor_signal"],[4,2,1,"","get_signal_names"],[4,2,1,"","make_monitor"],[4,2,1,"","record_signals"],[4,2,1,"","remove_monitor"],[4,2,1,"","reset_monitors"]],"names.Names":[[5,2,1,"","get_name_string"],[5,2,1,"","get_name_type"],[5,2,1,"","lookup"],[5,2,1,"","query"],[5,2,1,"","unique_error_codes"]],"network.Network":[[6,2,1,"","check_network"],[6,2,1,"","execute_clock"],[6,2,1,"","execute_d_type"],[6,2,1,"","execute_gate"],[6,2,1,"","execute_network"],[6,2,1,"","execute_switch"],[6,2,1,"","get_connected_output"],[6,2,1,"","get_input_signal"],[6,2,1,"","get_output_signal"],[6,2,1,"","invert_signal"],[6,2,1,"","make_connection"],[6,2,1,"","update_clocks"],[6,2,1,"","update_signal"]],"parse.Parser":[[7,2,1,"","add_connection"],[7,2,1,"","add_devices"],[7,2,1,"","add_monitors"],[7,2,1,"","get_next"],[7,2,1,"","parse_connection_block"],[7,2,1,"","parse_connection_statement"],[7,2,1,"","parse_device_block"],[7,2,1,"","parse_device_type"],[7,2,1,"","parse_devices_statement"],[7,2,1,"","parse_monitor_statement"],[7,2,1,"","parse_monitors_block"],[7,2,1,"","parse_network"],[7,2,1,"","parse_pin"],[7,2,1,"","skip_to_block"],[7,2,1,"","skip_to_end_of_line"],[7,2,1,"","throw_error"]],"scanner.Scanner":[[8,3,1,"","BLOCK_COMMENT_IDENTIFIERS"],[8,1,1,"","EOF"],[8,3,1,"","LINE_COMMENT_IDENTIFIER"],[8,2,1,"","get_line_by_lineno"],[8,2,1,"","get_line_by_pos"],[8,2,1,"","get_lineno_colno"],[8,2,1,"","get_next_character"],[8,2,1,"","get_next_chunk"],[8,2,1,"","get_next_name"],[8,2,1,"","get_next_non_whitespace_character"],[8,2,1,"","get_next_number"],[8,2,1,"","get_symbol"],[8,2,1,"","move_pointer_absolute"],[8,2,1,"","move_pointer_after_next_match"],[8,2,1,"","move_pointer_onto_next_character"],[8,2,1,"","move_pointer_relative"],[8,2,1,"","move_pointer_skip_whitespace_characters"],[8,4,1,"","pointer"],[8,4,1,"","pointer_colno"],[8,4,1,"","pointer_lineno"],[8,4,1,"","pointer_pos"],[8,2,1,"","read"]],"symbol_types.DTypeInputType":[[9,3,1,"","CLEAR"],[9,3,1,"","CLK"],[9,3,1,"","DATA"],[9,3,1,"","SET"]],"symbol_types.DTypeOutputType":[[9,3,1,"","Q"],[9,3,1,"","QBAR"]],"symbol_types.DeviceType":[[9,3,1,"","AND"],[9,3,1,"","CLOCK"],[9,3,1,"","D_TYPE"],[9,3,1,"","NAND"],[9,3,1,"","NOR"],[9,3,1,"","OR"],[9,3,1,"","SWITCH"],[9,3,1,"","XOR"]],"symbol_types.ExtendedEnum":[[9,2,1,"","values"]],"symbol_types.ExternalSymbolType":[[9,3,1,"","IDENTIFIER"],[9,3,1,"","NUMBERS"]],"symbol_types.KeywordType":[[9,3,1,"","CONNECTIONS"],[9,3,1,"","DEVICES"],[9,3,1,"","MONITORS"]],"symbol_types.OperatorType":[[9,3,1,"","COLON"],[9,3,1,"","COMMA"],[9,3,1,"","CONNECT"],[9,3,1,"","DOT"],[9,3,1,"","EQUAL"],[9,3,1,"","LEFT_ANGLE"],[9,3,1,"","RIGHT_ANGLE"],[9,3,1,"","SEMICOLON"]],"symbol_types.ReservedSymbolType":[[9,3,1,"","AND"],[9,3,1,"","CLEAR"],[9,3,1,"","CLK"],[9,3,1,"","CLOCK"],[9,3,1,"","COLON"],[9,3,1,"","COMMA"],[9,3,1,"","CONNECT"],[9,3,1,"","CONNECTIONS"],[9,3,1,"","DATA"],[9,3,1,"","DEVICES"],[9,3,1,"","DOT"],[9,3,1,"","D_TYPE"],[9,3,1,"","EQUAL"],[9,3,1,"","LEFT_ANGLE"],[9,3,1,"","MONITORS"],[9,3,1,"","NAND"],[9,3,1,"","NOR"],[9,3,1,"","OR"],[9,3,1,"","Q"],[9,3,1,"","QBAR"],[9,3,1,"","RIGHT_ANGLE"],[9,3,1,"","SEMICOLON"],[9,3,1,"","SET"],[9,3,1,"","SWITCH"],[9,3,1,"","XOR"],[9,3,1,"id0","symbol_contexts"]],"symbol_types.ReservedSymbolTypeMeta":[[9,4,1,"","mappings"],[9,2,1,"","values"]],devices:[[0,1,1,"","Device"],[0,1,1,"","Devices"]],exceptions:[[1,1,1,"","Errors"],[1,1,1,"","ParseBaseException"],[1,1,1,"","ParseBaseExceptionMeta"],[1,1,1,"","SemanticErrors"],[1,1,1,"","SyntaxErrors"]],monitors:[[4,1,1,"","Monitors"]],names:[[5,1,1,"","Names"]],network:[[6,1,1,"","Network"]],parse:[[7,1,1,"","Parser"]],scanner:[[8,1,1,"","Scanner"],[8,1,1,"","Symbol"]],symbol_types:[[9,1,1,"","DTypeInputType"],[9,1,1,"","DTypeOutputType"],[9,1,1,"","DeviceType"],[9,1,1,"","ExtendedEnum"],[9,1,1,"","ExternalSymbolType"],[9,1,1,"","KeywordType"],[9,1,1,"","OperatorType"],[9,1,1,"","ReservedSymbolType"],[9,1,1,"","ReservedSymbolTypeMeta"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","property","Python property"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:property"},terms:{"0":[0,4,7,8],"1":[7,8],"31":7,"break":8,"class":[1,5,7,8,9],"default":[0,1,8,9],"do":6,"enum":9,"float":1,"function":[0,4,5,6,8],"int":[0,4,5,8],"long":8,"new":[5,6,7],"public":0,"return":[0,1,4,5,6,7,8,9],"switch":[0,1,6,7,9],"true":[0,4,6,7,8],"while":1,A:8,AND:[6,7,9],If:[4,5,6,7,8],It:[0,5,7,8],No:[0,1],OR:[6,7,9],The:[0,4,6,7,8],about:6,absolut:8,accept:8,act:9,add:[0,1,4,5,6,7,9],add_connect:7,add_devic:[0,7],add_error:1,add_input:0,add_monitor:7,add_output:0,after:[4,8],all:[0,1,4,6,7,9],alloc:5,allow:[1,8,9],also:[5,8],an:[0,1,5,7,8,9],analys:7,ar:[4,5,6,7,8,9],around:9,attempt:1,attribut:9,base:[0,1,4,5,6,7,8,9],befor:[0,4,8],begin:0,being:4,between:[7,9],block:[7,9],block_comment_identifi:8,bool:8,build:[6,7],built:9,builtin:9,c:8,call:[4,7,8],callabl:8,can:8,caus:8,certain:8,charact:8,check:6,check_network:6,chunk:8,circuit:[1,7,8],classmethod:9,classnam:[1,9],clear:[4,7,9],clk:[7,9],clock:[0,1,6,7,9],clock_half_period:0,code:[1,5],cold:0,cold_startup:0,collect:1,colno:8,colon:9,column:8,combin:9,comma:9,comment:8,comparison:9,connect:[1,6,7,9],connectintoin:1,connection_stat:7,connectouttoout:1,consol:4,contain:[0,4,6],content:8,context:9,correct:[7,9],correspond:[0,4,5,6,9],creat:[0,1,9],criteria:8,current:[4,7,8],current_symbol:7,custom:9,cycl:[0,4,6],cycles_complet:4,d:[0,6,9],d_type:[7,9],data:[7,9],deal:[5,7],defin:[1,5,8,9],definit:[7,8,9],delet:4,demand:5,denot:8,descript:[1,7],desir:8,detect:7,devic:[1,3,4,6,7,9],device_definit:7,device_id:[0,4,6],device_kind:0,device_nam:7,device_name1:7,device_name2:7,device_properti:0,device_typ:7,devicetyp:[7,9],dictionari:[1,4,9],differ:[1,6],digit:7,digit_excluding_zero:7,direct:6,directli:[5,9],displai:4,display_sign:4,distanc:8,doc:1,doe:[4,6],dot:9,draw:4,dtype:[7,9],dtypeinputtyp:9,dtypeoutputtyp:9,duplic:1,e:[7,8],each:[4,5],ebnf:7,eg:7,either:[0,5,6,9],els:6,enabl:9,encapsul:8,end:[1,7,8],end_pred:8,entri:9,eof:[7,8],equal:9,error:[0,1,4,5,6,7],error_typ:7,everi:4,exampl:8,except:3,execut:6,execute_clock:6,execute_d_typ:6,execute_g:6,execute_network:6,execute_switch:6,exist:4,explain:1,explan:1,extendedenum:9,externalsymboltyp:[5,8,9],fall:6,fals:[6,7,8],fewer:8,file:[1,7,8],find:4,find_devic:0,first:6,first_device_id:6,first_port_id:6,flag:8,flip:9,floatinginput:1,flop:9,follow:8,form:6,format:8,found:[1,7],from:[0,4,6,7,8,9],gate:[0,1,6],gate_typ:7,get:[6,7,8],get_connected_output:6,get_devic:0,get_input_sign:6,get_line_by_lineno:8,get_line_by_po:8,get_lineno_colno:8,get_margin:4,get_monitor_sign:4,get_name_str:5,get_name_typ:5,get_next:7,get_next_charact:8,get_next_chunk:8,get_next_nam:8,get_next_non_whitespace_charact:8,get_next_numb:8,get_output_sign:6,get_signal_id:0,get_signal_nam:[0,4],get_symbol:8,give:7,given:[6,8],grammat:5,greater:8,gui:3,half:0,handl:[1,7],have:9,help:7,high:6,how:4,i:[7,8],id:[0,4,5,6,8],identifi:9,in_pin:7,includ:8,index:[3,5,8],indic:8,indirectli:[5,9],inform:6,initi:[0,8,9],initial_st:0,input:[0,1,6,8,9],input_id:[0,6],instanc:[0,4,6,7,8],instead:8,integ:[0,5],interfac:9,intern:5,invalid:[0,1,6],invalidandparam:1,invalidclockparam:1,invalidswitchparam:1,invers:6,invert_sign:6,irrelev:8,isdigit:8,its:[0,6,8],keep:5,keyword:[5,7,9],keywordtyp:[7,9],lambda:8,languag:9,larger:8,last:8,least:8,leav:4,left:8,left_angl:9,length:[4,8],letter:8,level:[4,6],line:[7,8],line_comment_identifi:8,lineno:8,list:[0,1,4,5,7,9],logic:[0,1,4,5,6,7,8,9],longest:4,look:5,lookup:5,low:[0,6],mainli:1,make:[0,8],make_clock:0,make_connect:6,make_d_typ:0,make_devic:0,make_g:0,make_monitor:4,make_switch:0,mani:[0,6],map:[5,9],mappingproxi:9,meet:8,memori:[0,4],messag:[1,7],metaclass:[1,9],method:[0,9],miss:1,missingparam:1,missingsemicolon:1,mixtur:8,modul:3,monitor:[1,3,7,9],monitor_stat:7,monitorinputpin:1,monitorsamepin:1,most:[5,9],move:[7,8],move_pointer_absolut:8,move_pointer_after_next_match:8,move_pointer_onto_next_charact:8,move_pointer_rel:8,move_pointer_skip_whitespace_charact:8,much:4,multipl:1,multipleconnect:1,n:8,name:[0,1,3,4,6,7,8],name_id:5,name_str:5,name_string_list:5,nameclash:1,nand:[6,7,9],network:[0,3,4,7],next:[7,8],no_error:[0,4,6],no_of_input:0,noconnect:1,nodevic:1,nomonitor:1,non:8,none:[0,1,4,5,6,7,8],nor:[6,7,9],note:[6,8],num_error_cod:5,number:[0,1,5,7,8,9],object:[0,1,4,5,6,7,8,9],ok:7,old:6,onc:8,one:[6,8],onli:8,onto:8,oper:9,operatortyp:9,option:[1,4,5,7,8],origin:9,oscil:6,other:5,out:[4,7],out_pin1:7,out_pin2:7,out_pin:7,output:[0,1,4,6,9],output_id:[0,4,6],over:8,page:3,pair:6,paramet:[0,1,4,6,7,8],pars:[1,7],parse_connection_block:7,parse_connection_stat:7,parse_device_block:7,parse_device_stat:7,parse_device_typ:7,parse_devices_stat:7,parse_monitor_stat:7,parse_monitors_block:7,parse_monitors_stat:7,parse_network:7,parse_pin:7,parsebaseexcept:1,parsebaseexceptionmeta:1,parser:[1,3,8],pass:8,path:8,period:[0,1],pin1:7,pin2:7,pin:[1,7],pin_nam:7,pin_name1:7,pin_name2:7,po:8,point:[0,9],pointer:8,pointer_colno:8,pointer_lineno:8,pointer_po:8,port:[0,4,6],port_id:0,posit:8,predic:8,present:5,press:6,pretti:1,prevent:8,print:1,print_error_messag:1,project:[0,1,4,5,6,7,8,9],properti:[0,8,9],protect:8,provid:5,q:[7,9],qbar:[7,9],queri:5,random:0,reach:[7,8],read:8,receiv:7,record:4,record_sign:4,recov:7,rel:8,remov:4,remove_monitor:4,requir:6,reserv:9,reservedsymboltyp:[5,8,9],reservedsymboltypemeta:9,reset:8,reset_monitor:4,reset_point:8,retriev:7,right_angl:9,rise:6,rule:6,s:[4,8],scanner:[1,3,7],search:3,second:6,second_device_id:6,second_port_id:6,self:[0,1,4,6,7,8],semant:[1,7],semanticerror:1,semicolon:[7,9],sequenc:8,set:[0,4,6,7,9],set_switch:0,sever:9,signal:[0,4,6],signal_nam:0,similar:9,simplifi:1,simul:[0,1,4,5,6,7,8,9],singl:1,skip:[7,8],skip_to_block:7,skip_to_end_of_lin:7,so:6,space:[4,8],specif:8,specifi:[0,4,6,8,9],standard:9,start:[0,4,8],start_pred:8,state:[0,4],statement:[1,7],steady_st:6,store:[0,4,5,8],str:[1,5,8],string:[0,1,5,7,8,9],subclass:9,subsequ:8,success:[0,4,6,7],successfulli:7,suppli:8,support:9,switch_stat:[0,6],symbol:[1,7,8,9],symbol_context:9,symbol_id:8,symbol_typ:[3,5,7,8],syntact:7,syntax:[1,7],syntaxerror:1,target:[6,8],text:4,than:8,them:8,thi:[0,1,4,5,6,7,8,9],throw_error:7,time:6,togeth:[6,9],token:1,trace:4,track:5,translat:8,tri:7,tupl:8,two:4,type:[0,1,5,6,7,8,9],unconnect:6,undefin:1,undefineddevic:1,undefinedinpin:1,undefinedoutpin:1,unexpect:[1,7],unexpectedeof:1,unexpectedparam:1,unexpectedtoken:1,union:[5,8],uniqu:5,unique_error_cod:5,unsuccess:0,until:7,up:[0,5,8],updat:[6,7],update_clock:6,update_sign:6,upto:8,us:[0,1,4,5,6,7,8,9],usabl:8,user:[5,9],valid:[7,8],valu:[6,8,9],variabl:5,wa:7,warn:1,when:8,whether:8,which:[5,8,9],whitespac:8,without:8,word:5,wrapper:9,x:6,xor:[6,7,9],y:6,zero:8},titles:["devices module","exceptions module","gui module","Logic Simulator Documnetation","monitors module","names module","network module","parser module","scanner module","symbol_types module"],titleterms:{"class":[0,4,6],content:3,devic:0,documnet:3,except:1,gui:2,indic:3,logic:3,modul:[0,1,2,4,5,6,7,8,9],monitor:4,name:5,network:6,parser:7,scanner:8,simul:3,symbol_typ:9,tabl:3}})