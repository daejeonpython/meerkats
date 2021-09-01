import datetime

a = ['2021-01-01', '2021-12-31']
b = '2021.1.1~12.31.'


def date_to_str(obj):
    date_time_obj = datetime.datetime.strptime(obj,'%Y-%m-%d')
    date_time_obj = date_time_obj.strftime('%Y. %#m .%#d')
    return date_time_obj


for i in a:
    result = date_to_str(i)
    print(result)
ghlr

def precision_recall_curve_plot(y_test, pred_proba_c1):
    ## threshold ndarray와 이 threshold에 따른 정밀도, 재현율 ndarray 추출.
    precisions, recalls, thresholds = precision_recall_curve(y_test, pred_proba_c1)

    # X축을 threshold값으로 y축은 정밀도. 재현율 값으로 각각 plot 수행. 정밀도는 점선으로 표시함
    plt.figure(figsize=(8, 6))

    threshold_boundary = thresholds.shape[0]

    plt.plot(thresholds, precisions[0:threshold_boundary], linestyle='--', label='precision')
    plt.plot(thresholds, recalls[0:threshold_boundary], label='recall')

    # threshold 값 x축의 scale을 0.1 단위로 변경

    start, end = plt.xlim()
    plt.xticks(np.round(np.arange(start, end, 0.1), 2))

    ## x축, y축 label과 legend, 그리고 grid 설정
    plt.xlabel('Threshold value');
    plt.ylabel('Precision and Recall value')
    plt.legend();
    plt.grid()
    plt.show()


def get_clf_eval(y_test, pred=None, pred_proba = None):
    confusion = confusion_matrix(y_test, pred)

    accuracy = accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred)
    recall = recall_score(y_test, pred)

    ## f1 스코어 추가
    f1 = f1_score(y_test, pred)

    # ROC-AUC 추가
    roc_auc = roc_auc_score(y_test, pred_proba)
    print('오차행렬')
    print(confusion)

    ## f1 score print 추가

    print('정확도:{0:.4f}, 정밀도:{1:.4f}, 재현율:{2:.4f}, F1:{3:.4f}, AUC:{4:.4f}'.format(accuracy, precision, recall, f1, roc_auc))


def get_eval_by_threshold(y_test, pred_proba_c1, thresholds):
    ## threshold list 객체 내의 값을 차례로 iteration하면서 Evaluation 수행
    for custom_threshold in thresholds:
        binarizer = Binarizer(threshold=custom_threshold).fit(pred_proba_c1)
        custom_predict = binarizer.transform(pred_proba_c1)

        print('임곗값:', custom_threshold)
        get_clf_eval(y_test, custom_predict)