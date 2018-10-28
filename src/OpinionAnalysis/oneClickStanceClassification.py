import numpy as np
from hanziconv import HanziConv
from nltk.tokenize import RegexpTokenizer
from scipy import spatial
import jieba
# jieba.enable_parallel(120)
import xgboost as xgb
import pickle
# from gensim.models import word2vec
# def LoadModel(modelFilename, binOrNot=False):
# 	model = word2vec.KeyedVectors.load_word2vec_format(modelFilename, binary=binOrNot)
# 	return model

def removePunctuation(_str):
	tokenizer = RegexpTokenizer(r'\w+')
	return ' '.join(tokenizer.tokenize(_str))

def cutWord(_str):
	return ' '.join([i for i in jieba.cut(removePunctuation(_str)) if not i == " "])

def averageSelfDefine2(weightList):
	_sum = 0.0
	counter = 0
	resultList = [0.0]*len(weightList)
	for weight in weightList:
		if abs(weight) > 0:
			counter += 1
			_sum += abs(weight)
	if counter > 0:
		for index in range(len(weightList)):
			resultList[index] = weightList[index]/_sum
	else: #if all zero weight => see as equal weights
		for index in range(len(weightList)):
			resultList[index] = 1/len(resultList)
	return resultList

def checkAllZero(targetList):
	for ele in targetList:
		if not ele == 0.0:
			return False
	return True

def checkNegativeToken(_content):
	# negativeDict = {"不支持":"支持", "反對":"要", "不贊成":"贊成", "不同意":"同意", "阻擋":"推進"}
	polarityList = ["不支持", "反對", "不贊成", "不同意", "阻擋",
					"不同意", "不贊同","不響應","不附和","不採納",
					"不擁護","不點頭 ","不苟同","抗議","唱反調",
					"不允許","不承諾","不准許","不容許","不答應 ",
					"不應該","阻止","抵制"]
	polarityListPos = ["支持", "要", "贊成", "同意", "推進",
						"同意", "贊同","響應","附和","採納",
						"擁護","點頭 ","苟同","同意","贊成",
						"允許","承諾","准許","容許","答應 ",
						"應該","推進","支持"]
	negativeStanceNum = 0
	newContent = _content
	for index in range(len(polarityList)):
		if polarityList[index] in _content:
			negativeStanceNum += newContent.count(polarityList[index])
			newContent = newContent.replace(polarityList[index], polarityListPos[index])

	# for key in negativeDict:
	# 	if key in _content:
	# 		newContent = _content.replace(key, negativeDict[key])
	# 		return True, newContent
	# return False, _content
	if negativeStanceNum%2 == 0:
		return False, newContent
	else:
		return True, newContent

#Attention mechnism function
def matchFunc(titleText, bodyText, vocabList, word2vecModel):
	weightList = list()
	applyNegMechanism = True
	if applyNegMechanism:
		negOrNot, titleText = checkNegativeToken(titleText)
		# print("{}\t{}".format(negOrNot, titleText))
	titleWordList = cutWord(titleText).split()
	bodyWordList = cutWord(bodyText).split()
	resultList = list()
	wordCounter1 = 0
	wordCounter2 = 0
	_MAX_wmd = 100
	zeroEmbedding = [0.0]*len(word2vecModel["這"])

	#count title sentence embedding
	titleEmbedding = list(zeroEmbedding)
	for word in titleWordList:
		if word in vocabList:
			wordCounter1 += 1
			titleEmbedding = np.add(titleEmbedding, word2vecModel[word])
		elif HanziConv.toSimplified(word) in vocabList:
			wordCounter1 += 1
			titleEmbedding = np.add(titleEmbedding, word2vecModel[HanziConv.toSimplified(word)])
	if wordCounter1 > 0:
		titleEmbedding = np.array(titleEmbedding)/wordCounter1
	resultList.append(titleEmbedding)

	# Output the cos sim of the embedding of the word in body text and 
	# the embedding of title(word embedding sum)
	for word in bodyWordList:
		if checkAllZero(titleEmbedding):
			weightList.append(0.0)
		elif (not word in vocabList) and (not HanziConv.toSimplified(word) in vocabList):
			weightList.append(0.0)
		else:
			if word in vocabList:
				weightList.append(1-spatial.distance.cosine(titleEmbedding, word2vecModel[word]))
			else:
				weightList.append(1-spatial.distance.cosine(titleEmbedding, word2vecModel[HanziConv.toSimplified(word)]))

	weightList = averageSelfDefine2(weightList)
	if applyNegMechanism and negOrNot:
			weightList = [-1*ele for ele in weightList]

	resultEmbedding = list(zeroEmbedding)
	for index in range(len(bodyWordList)):
		if bodyWordList[index] in vocabList:
			resultEmbedding = np.add(resultEmbedding, 
									np.dot(word2vecModel[bodyWordList[index]], weightList[index]))
		elif HanziConv.toSimplified(bodyWordList[index]) in vocabList:
			resultEmbedding = np.add(resultEmbedding, 
									np.dot(word2vecModel[HanziConv.toSimplified(bodyWordList[index])], 
											weightList[index]))
	resultList.append(resultEmbedding)

	resultList.append([min(word2vecModel.wmdistance(titleWordList, bodyWordList), _MAX_wmd)])
	if checkAllZero(titleEmbedding) or checkAllZero(resultEmbedding):
		resultList.append([0.0])
	else:
		resultList.append([1-spatial.distance.cosine(titleEmbedding, resultEmbedding)])
	return np.concatenate(resultList, axis=0)

def stanceAnalyzerCos(queryText, bodyText, w2v):
	w2vModel = w2v
	w2vModelVocab = w2vModel.vocab

	test_x = list()
	# queryText = "台灣應進口美國牛肉" 
	# bodyText = "美牛瘦肉精解禁議題發燒，10日上午主婦聯盟環境保護基金會台中分會串聯多個中部團體出面反對瘦肉精解禁，呼籲台中市長胡志強捍衛市民健康，一起反瘦肉精，並加強市售進口牛肉的查驗，以保障國民健康。 台中一年抽驗14件牛肉太離譜 宜蘭和南部五縣市首長皆已挺身反對瘦肉精解禁，中部團體齊聚市府前質問台中市長胡志強的立場，並聯合要求台中市政府公布最近一年檢驗市售進口牛肉是否含瘦肉精，結果台中市衛生局資料顯示，去年共抽驗14件市售牛肉，有3 件含瘦肉精，不合格率為21%。主婦聯盟台中分會表示，全台中市有數百家賣場超市及傳統市場販賣美牛，一年只抽檢14 件太離譜，平均一個月才抽驗一件！所謂「三管五卡」在管市場這端，地方衛生單位嚴重失職，根本未用力為消費者把關！ 衛生局不願代檢市售美牛 主婦聯盟台中分會對衛生局抽驗市售牛肉件數過低表示不滿，因此從台中市多家大賣場和超市購買市售美國牛肉，要送交衛生局檢驗瘦肉精，但到場的台中市衛生局陳淑惠科長不願意帶回檢驗，要民間自行送檢驗機構，並表示衛生局會到市面上購買抽驗。對於台中市今年會抽驗幾件美牛，不願具體回應，只表示會比去年多，隨即快閃走人，連媒體想詢問衛生局如何採樣抽驗都問不到。 市售進口牛肉含瘦肉精比例高達二成 主婦聯盟台中分會主任楊淑慧表示，台灣瘦肉精政策尚未解禁，市售進口牛肉就已經高達23成含禁用的瘦肉精，已使國人健康置身風險之中，如何保障消費者安全？另政府研擬含瘦肉精美牛要比照香菸標示警語，恐怕警告不敵價格，瘦肉精危害國民健康，恐怕日後會增加國民健保支出。 台灣生態學會秘書長蔡智豪表示，中央有意開放含瘦肉精美牛，地方政府應明確拒絕，目前美國牛肉進口時，海關抽檢無法百分百把關，市面上仍買得到含瘦肉精的美國牛肉，地方政府應加強檢驗，為食的安全嚴格把關。 人本教育基金會中部聯合辦公室張碧華主任說，蔡炳坤副市長已表示市府會加強稽查檢驗美國牛肉和相關產品，不讓有瘦肉精的產品流入市面。希望台中市政府能確實執行，保障國人飲食安全。台灣主婦聯盟生活消費合作社中社經理張月瑩也強調，政府應將消費者的健康安全放在第一位，為國民的飲食健康做好嚴格的把關。 張豐年醫師表示，不論在動物實驗或台灣發生的病例，已顯示瘦肉精的高度風險性。且目前全球尚無充分的人體實驗研究結果，若貿然開放含瘦肉精的美國牛肉進口，勢必會對國人的健康有嚴重的危害。 中部團體在中市府前高喊「反美牛、反瘦肉精」、「捍衛國人健康　反對瘦肉精解禁!」，表達民間反對政府棄守禁用瘦肉精政策，請中央和地方都硬起來，向美國瘦肉精說不。 市售美牛有多少含瘦肉精？ 依照以上資料，市售進口牛肉很可能每56件就有一件含瘦肉精，顯見政府信誓旦旦的三管五卡早已破功，不僅在海關的抽驗比例過低，進入市場後的抽驗比例更離譜到一個月抽不到五件，難怪媒體隨便在大賣場買美牛就驗出含瘦肉精！主婦聯盟台中分會在結束發聲行動後表示，會將所購美牛送交檢驗單位檢驗，預定下周公布檢驗結果，看看民間自行送驗的結果如何。 參與團體： 主婦聯盟環境保護基金會台中分會、台灣生態學會、台灣主婦聯盟生活消費合作社台中分社、台中市新環境促進會、人本教育基金會中部聯合辦公室、台中市原鄉文化協會、牛罵頭文化協進會、台灣中社、台中醫界聯盟、彰化醫界聯盟、大肚山永續發展工作室等,三管五卡攏是假！中市一年只抽驗14件牛肉 瘦肉精管不了卡不住！NGO反對瘦肉精解禁"

	# generate features
	resultFeatures = matchFunc(queryText, bodyText , w2vModelVocab, w2vModel)
	# resultFeatures2 = matchFunc(bodyText, queryText , w2vModelVocab, w2vModel)
	# resultFeatures = np.append(resultFeatures, resultFeatures2)
	test_x.append(resultFeatures)
	dtest = xgb.DMatrix(test_x)

	foldValid = True
	Label = 3
	# modelFilename = "./OpinionAnalysis/XGBoost3_F0_Att2trainChineseW2V_D300W5MC2_v2BiWay.pickle"
	# modelFilename = "/dhome/b01901130/stanceEmbedding/Chinese-Discovery-News-master/src/OpinionAnalysis/XGBoost3_F0_Att2ChinesenoWeight5Fold_v4.pickle"
	# modelFilename = "/dhome/b01901130/stanceEmbedding/Chinese-Discovery-News-master/src/OpinionAnalysis/XGBoost3_F0_Att2ChineseWeighted1_v5.pickle"
	# modelFilename = "/dhome/b01901130/stanceEmbedding/Chinese-Discovery-News-master/src/OpinionAnalysis/XGBoost3_F0_Att2ChineseWeighted15Fold_v5.pickle"
	modelFilename = "/dhome/b01901130/stanceEmbedding/Chinese-Discovery-News-master/src/OpinionAnalysis/XGBoost3_F0_Att2ChineseWeighted15Fold_v8NEGEP2000_v2.pickle"
	with open(modelFilename, "rb") as f:
		pickleLoad = pickle.load(f)
	bst = pickleLoad[0]

	if not foldValid:
		pred_y = bst.predict(dtest)
		pred_y = pred_y.reshape(len(test_x), Label)
	else:
		pred_y = kfoldPredict(bst, dtest, Label, len(test_x))
	print(pred_y)
	pred_y = np.argmax(pred_y, axis=1)
	labelList = ["disagree", "agree", "discuss"]
	_stance = labelList[int(pred_y[0])]
	# for index in range(len(test_x)):
	# 	_stance = labelList[int(pred_y[index])]
	#	print("============ stance : {} =============".format(_stance))
	return _stance

def kfoldPredict(bstModelList, testDMatrix, Label, testCaseNum):
	resultPredY = list()
	for bst in bstModelList:
		pred_y = bst.predict(testDMatrix, ntree_limit=bst.best_ntree_limit)
		pred_y = pred_y.reshape(testCaseNum, Label)
		if len(resultPredY) == 0:
			resultPredY = pred_y
		else:
			resultPredY = resultPredY+pred_y
	resultPredY = resultPredY/len(bstModelList)
	return resultPredY

def stanceAnalyzer(queryText, bodyText, w2v):
	w2vModel = w2v
	w2vModelVocab = w2vModel.vocab

	test_x = list()
	# queryText = "台灣應進口美國牛肉" 
	# bodyText = "美牛瘦肉精解禁議題發燒，10日上午主婦聯盟環境保護基金會台中分會串聯多個中部團體出面反對瘦肉精解禁，呼籲台中市長胡志強捍衛市民健康，一起反瘦肉精，並加強市售進口牛肉的查驗，以保障國民健康。 台中一年抽驗14件牛肉太離譜 宜蘭和南部五縣市首長皆已挺身反對瘦肉精解禁，中部團體齊聚市府前質問台中市長胡志強的立場，並聯合要求台中市政府公布最近一年檢驗市售進口牛肉是否含瘦肉精，結果台中市衛生局資料顯示，去年共抽驗14件市售牛肉，有3 件含瘦肉精，不合格率為21%。主婦聯盟台中分會表示，全台中市有數百家賣場超市及傳統市場販賣美牛，一年只抽檢14 件太離譜，平均一個月才抽驗一件！所謂「三管五卡」在管市場這端，地方衛生單位嚴重失職，根本未用力為消費者把關！ 衛生局不願代檢市售美牛 主婦聯盟台中分會對衛生局抽驗市售牛肉件數過低表示不滿，因此從台中市多家大賣場和超市購買市售美國牛肉，要送交衛生局檢驗瘦肉精，但到場的台中市衛生局陳淑惠科長不願意帶回檢驗，要民間自行送檢驗機構，並表示衛生局會到市面上購買抽驗。對於台中市今年會抽驗幾件美牛，不願具體回應，只表示會比去年多，隨即快閃走人，連媒體想詢問衛生局如何採樣抽驗都問不到。 市售進口牛肉含瘦肉精比例高達二成 主婦聯盟台中分會主任楊淑慧表示，台灣瘦肉精政策尚未解禁，市售進口牛肉就已經高達23成含禁用的瘦肉精，已使國人健康置身風險之中，如何保障消費者安全？另政府研擬含瘦肉精美牛要比照香菸標示警語，恐怕警告不敵價格，瘦肉精危害國民健康，恐怕日後會增加國民健保支出。 台灣生態學會秘書長蔡智豪表示，中央有意開放含瘦肉精美牛，地方政府應明確拒絕，目前美國牛肉進口時，海關抽檢無法百分百把關，市面上仍買得到含瘦肉精的美國牛肉，地方政府應加強檢驗，為食的安全嚴格把關。 人本教育基金會中部聯合辦公室張碧華主任說，蔡炳坤副市長已表示市府會加強稽查檢驗美國牛肉和相關產品，不讓有瘦肉精的產品流入市面。希望台中市政府能確實執行，保障國人飲食安全。台灣主婦聯盟生活消費合作社中社經理張月瑩也強調，政府應將消費者的健康安全放在第一位，為國民的飲食健康做好嚴格的把關。 張豐年醫師表示，不論在動物實驗或台灣發生的病例，已顯示瘦肉精的高度風險性。且目前全球尚無充分的人體實驗研究結果，若貿然開放含瘦肉精的美國牛肉進口，勢必會對國人的健康有嚴重的危害。 中部團體在中市府前高喊「反美牛、反瘦肉精」、「捍衛國人健康　反對瘦肉精解禁!」，表達民間反對政府棄守禁用瘦肉精政策，請中央和地方都硬起來，向美國瘦肉精說不。 市售美牛有多少含瘦肉精？ 依照以上資料，市售進口牛肉很可能每56件就有一件含瘦肉精，顯見政府信誓旦旦的三管五卡早已破功，不僅在海關的抽驗比例過低，進入市場後的抽驗比例更離譜到一個月抽不到五件，難怪媒體隨便在大賣場買美牛就驗出含瘦肉精！主婦聯盟台中分會在結束發聲行動後表示，會將所購美牛送交檢驗單位檢驗，預定下周公布檢驗結果，看看民間自行送驗的結果如何。 參與團體： 主婦聯盟環境保護基金會台中分會、台灣生態學會、台灣主婦聯盟生活消費合作社台中分社、台中市新環境促進會、人本教育基金會中部聯合辦公室、台中市原鄉文化協會、牛罵頭文化協進會、台灣中社、台中醫界聯盟、彰化醫界聯盟、大肚山永續發展工作室等,三管五卡攏是假！中市一年只抽驗14件牛肉 瘦肉精管不了卡不住！NGO反對瘦肉精解禁"

	# generate features
	resultFeatures = matchFunc(queryText, bodyText , w2vModelVocab, w2vModel)
	# resultFeatures2 = matchFunc(bodyText, queryText , w2vModelVocab, w2vModel)
	# resultFeatures = np.append(resultFeatures, resultFeatures2)
	test_x.append(resultFeatures)
	dtest = xgb.DMatrix(test_x)

	#cos sim attention model
	foldValid = True
	Label = 3
	# modelCosFilename = "./OpinionAnalysis/XGBoost3_F0_Att2trainChineseW2V_D300W5MC2_v2BiWay.pickle"
	# modelCosFilename = "./OpinionAnalysis/XGBoost3_F0_Att2ChineseBiWayWeighted15Fold.pickle"
	# modelCosFilename = "XGBoost3_F0_Att2ChineseBiWayWeighted15Fold.pickle"
	modelCosFilename = "/dhome/b01901130/stanceEmbedding/Chinese-Discovery-News-master/src/OpinionAnalysis/XGBoost3_F0_Att2ChinesenoWeight5Fold_v4.pickle"
	with open(modelCosFilename, "rb") as f:
		pickleLoad = pickle.load(f)
	bstCos = pickleLoad[0]

	if not foldValid:
		pred_y = bstCos.predict(dtest)
		pred_y = pred_y.reshape(len(test_x), Label)
	else:
		pred_y = kfoldPredict(bstCos, dtest, Label, len(test_x))
	pred_yCos = pred_y
	print(pred_yCos)
	pred_y = np.argmax(pred_y, axis=1)
	labelList = ["disagree", "agree", "discuss"]
	_stanceCos = labelList[int(pred_y[0])]
	
	# TSPW model
	# modelTSPWFilename = "./OpinionAnalysis/XGBoostSemiRetrain3_F0_Att2trainChineseW2V_D300W5MC2_v2BiWay.pickle"
	# modelTSPWFilename = "./OpinionAnalysis/XGBoostSemiRetrain3_F0_Att2ChineseBiWaynoWeight5Fold.pickle"
	# modelTSPWFilename = "XGBoostSemiRetrain3_F0_Att2ChineseBiWaynoWeight5Fold.pickle"
	modelTSPWFilename = "/dhome/b01901130/stanceEmbedding/Chinese-Discovery-News-master/src/OpinionAnalysis/XGBoostRetrain3_F0_Att2ChinesenoWeight5Fold_v4.pickle"
	with open(modelTSPWFilename, "rb") as f:
		pickleLoad = pickle.load(f)
	bstTSPW = pickleLoad[0]

	if not foldValid:
		pred_y = bstTSPW.predict(dtest)
		pred_y = pred_y.reshape(len(test_x), Label)
	else:
		pred_y = kfoldPredict(bstTSPW, dtest, Label, len(test_x))
	pred_yTSPW = pred_y
	print(pred_yTSPW)
	pred_y = np.argmax(pred_y, axis=1)
	_stanceTSPW = labelList[int(pred_y[0])]
	print("COS : {}\tTSPW : {}".format(_stanceCos, _stanceTSPW))

	pred_y = pred_yCos + pred_yTSPW
	print(pred_y)
	pred_y = np.argmax(pred_y, axis=1)
	_stanceEnsemble = labelList[int(pred_y[0])]
	print("Total : {}".format(_stanceEnsemble))
	if _stanceCos == _stanceTSPW:
		_stance = _stanceCos
	else:
		_stance = labelList[2]
	return _stance
	# return _stanceEnsemble

# W2V = LoadModel("/tmp3/r05922037/embedding/wiki.zh.self.bin", True)
# # queryTextT = "台灣應進口美國牛肉" 
# # bodyTextT = "美牛瘦肉精解禁議題發燒，10日上午主婦聯盟環境保護基金會台中分會串聯多個中部團體出面反對瘦肉精解禁，呼籲台中市長胡志強捍衛市民健康，一起反瘦肉精，並加強市售進口牛肉的查驗，以保障國民健康。 台中一年抽驗14件牛肉太離譜 宜蘭和南部五縣市首長皆已挺身反對瘦肉精解禁，中部團體齊聚市府前質問台中市長胡志強的立場，並聯合要求台中市政府公布最近一年檢驗市售進口牛肉是否含瘦肉精，結果台中市衛生局資料顯示，去年共抽驗14件市售牛肉，有3 件含瘦肉精，不合格率為21%。主婦聯盟台中分會表示，全台中市有數百家賣場超市及傳統市場販賣美牛，一年只抽檢14 件太離譜，平均一個月才抽驗一件！所謂「三管五卡」在管市場這端，地方衛生單位嚴重失職，根本未用力為消費者把關！ 衛生局不願代檢市售美牛 主婦聯盟台中分會對衛生局抽驗市售牛肉件數過低表示不滿，因此從台中市多家大賣場和超市購買市售美國牛肉，要送交衛生局檢驗瘦肉精，但到場的台中市衛生局陳淑惠科長不願意帶回檢驗，要民間自行送檢驗機構，並表示衛生局會到市面上購買抽驗。對於台中市今年會抽驗幾件美牛，不願具體回應，只表示會比去年多，隨即快閃走人，連媒體想詢問衛生局如何採樣抽驗都問不到。 市售進口牛肉含瘦肉精比例高達二成 主婦聯盟台中分會主任楊淑慧表示，台灣瘦肉精政策尚未解禁，市售進口牛肉就已經高達23成含禁用的瘦肉精，已使國人健康置身風險之中，如何保障消費者安全？另政府研擬含瘦肉精美牛要比照香菸標示警語，恐怕警告不敵價格，瘦肉精危害國民健康，恐怕日後會增加國民健保支出。 台灣生態學會秘書長蔡智豪表示，中央有意開放含瘦肉精美牛，地方政府應明確拒絕，目前美國牛肉進口時，海關抽檢無法百分百把關，市面上仍買得到含瘦肉精的美國牛肉，地方政府應加強檢驗，為食的安全嚴格把關。 人本教育基金會中部聯合辦公室張碧華主任說，蔡炳坤副市長已表示市府會加強稽查檢驗美國牛肉和相關產品，不讓有瘦肉精的產品流入市面。希望台中市政府能確實執行，保障國人飲食安全。台灣主婦聯盟生活消費合作社中社經理張月瑩也強調，政府應將消費者的健康安全放在第一位，為國民的飲食健康做好嚴格的把關。 張豐年醫師表示，不論在動物實驗或台灣發生的病例，已顯示瘦肉精的高度風險性。且目前全球尚無充分的人體實驗研究結果，若貿然開放含瘦肉精的美國牛肉進口，勢必會對國人的健康有嚴重的危害。 中部團體在中市府前高喊「反美牛、反瘦肉精」、「捍衛國人健康　反對瘦肉精解禁!」，表達民間反對政府棄守禁用瘦肉精政策，請中央和地方都硬起來，向美國瘦肉精說不。 市售美牛有多少含瘦肉精？ 依照以上資料，市售進口牛肉很可能每56件就有一件含瘦肉精，顯見政府信誓旦旦的三管五卡早已破功，不僅在海關的抽驗比例過低，進入市場後的抽驗比例更離譜到一個月抽不到五件，難怪媒體隨便在大賣場買美牛就驗出含瘦肉精！主婦聯盟台中分會在結束發聲行動後表示，會將所購美牛送交檢驗單位檢驗，預定下周公布檢驗結果，看看民間自行送驗的結果如何。 參與團體： 主婦聯盟環境保護基金會台中分會、台灣生態學會、台灣主婦聯盟生活消費合作社台中分社、台中市新環境促進會、人本教育基金會中部聯合辦公室、台中市原鄉文化協會、牛罵頭文化協進會、台灣中社、台中醫界聯盟、彰化醫界聯盟、大肚山永續發展工作室等,三管五卡攏是假！中市一年只抽驗14件牛肉 瘦肉精管不了卡不住！NGO反對瘦肉精解禁"
# queryTextT = "多元成家是普世價值" 
# bodyTextT = "婚姻平權 賴清德：不放棄在今年提方案 （中央社記者王承中台北6日電）行政院長賴清德今天針對婚姻平權表示，行政院目前正積極推動，沒有放棄在今年年底前能提出方案，他擔任行政院長面對這個重大政策，不會拖延，會盡力推動。"
# print(stanceAnalyzer(queryTextT, bodyTextT, W2V))
# print(stanceAnalyzerCos(queryTextT, bodyTextT, W2V))
