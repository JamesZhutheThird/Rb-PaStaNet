import pickle
hoi_id = 0
gt_bbox = pickle.load(open('-Results/gt_hoi_py2/hoi_%d.pkl' % hoi_id, 'rb'))
print(gt_bbox)
if 3390 in gt_bbox:
    print('yes')
