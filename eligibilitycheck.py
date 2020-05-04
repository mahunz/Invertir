def eligibilitycheck(dfformatted):
#    legiblestock = True
    reasonlist=[]
    IncluirLista = False
    # print (dfformatted)
    # EPS increases over the year (consistent)
    listagrow = []
    for growth in dfformatted.epsgrowth:
        if growth<0:
            listagrow.append(str(round(growth*100,2)) +'%')
            IncluirLista = True
    #        legiblestock = False
    if IncluirLista:
            reasonlist.append('EPSgrowth negativo = ' + str(listagrow).strip('[]'))
            #break
    # ROE > 0.15
    if dfformatted.roe.mean()<0.13:
#            legiblestock = False
            reasonlist.append('ROE promedio es menor que 13% ROE promedio = '+ str(round(dfformatted.roe.mean()*100,2)) +'%')
    # ROA > 0.07 (also consider debt to equity cause Assets = liabilities + equity)
    if dfformatted.roa.mean()<0.07:
#            legiblestock = False
            reasonlist.append('ROA promedio es menor que 7% ROA promedio = ' + str(round(dfformatted.roa.mean()*100,2)) +'%')
    # Long term debt < 5 * income
    if dfformatted.longtermdebt.tail(1).values[0]>5*dfformatted.netincome.tail(1).values[0]:
#            legiblestock = False
             reasonlist.append('La deuda a largo plazo es mayor a 5 veces el ingreso neto del último año = ' + str(round(dfformatted.longtermdebt.tail(1).values[0]/dfformatted.netincome.tail(1).values[0],2)))
    # Interest Coverage Ratio > 3
    if dfformatted.interestcoverageratio.tail(1).values[0]<3:
#            legiblestock = False
            reasonlist.append('El indicador cobertura de interes es menor a 3. InterestCovertRatio = ') + str(dfformatted.interestcoverageratio.tail(1).values[0])
            print(dfformatted.interestcoverageratio.tail(1).values[0])
#    print(reasonlist)
    return reasonlist