neonionApp.controller('WorkspaceDocumentCtrl', ['$scope', '$http', 'WorkspaceService', function ($scope, $http, WorkspaceService) {
    "use strict";

    $http.get('/api/workspace/documents/').success(function(data) {
        $scope.documents = data;
    });

    $scope.removeDocument = function (document) {
        var idx = $scope.documents.indexOf(document);
        // TODO add prompt
        WorkspaceService.removeDocument(document.urn);
        $scope.documents.splice(idx, 1);
    };
}]);

neonionApp.controller('WorkspaceImportCtrl', ['$scope', '$http', 'DocumentService', function ($scope, $http, DocumentService) {
    "use strict";

    $http.get('/documents/cms/list').success(function(data) {
        $scope.documents = data;
    });

    $scope.init = function () {
        $("#document-import-list").selectable();
    };

    $scope.importDocuments = function () {
        var selectedDocs = [];
        $('#document-import-list>.ui-selected').each(function() {
            selectedDocs.push(this.id);
        });
        DocumentService.importDocuments(selectedDocs);
    };

}]);

neonionApp.controller('AnnotationSetCtrl', ['$scope', '$http', function ($scope, $http) {
    "use strict";

    $http.get('/api/annotationsets').success(function(data) {
        $scope.annotationsets = data;
    });

}]);

neonionApp.controller('AnnotationStoreCtrl', ['$scope', '$http', function ($scope, $http) {
    "use strict";

    $http.get('/api/store/filter').success(function(data) {
        var occurrences = {};
        var filterUserData = data.rows;

        filterUserData.forEach(function(a) {
            var rdf = a.rdf;
            var key = a.quote + rdf;
            var ann = a.quote;
            var type = rdf.typeof;
            var date = a.created;
            var doc = a.uri;

            var typeParts = type.split('/');
            var concept = typeParts[typeParts.length-1];

            if (!(key in occurrences)) {
                occurrences[key] = {ann: ann, count:  1, typeof: concept, last: date, docs: new Array()};
            } else {
                occurrences[key].count++;
                var parsedDate = Date.parse(date);
                var parsedOld = Date.parse(occurrences[key].last);
                if (parsedDate > parsedOld) {
                    occurrences[key].last = date;
                }
            }

            if (((occurrences[key].docs).indexOf(doc)) == -1) {
                occurrences[key].docs.push(doc);
            }
        });
        $scope.occurrences = occurrences;
    });
}]);

neonionApp.controller('AnnOccurCtrl', ['$scope', '$http', '$location', function ($scope, $http, $location) {
    "use strict";
    var url = $location.absUrl().split('/');
    var quote = url[url.length-1];

    $http.get('/api/store/search?quote=' + quote).success(function (data) {
        var ann_occur = {};
        var filterUserData = data.rows;

        filterUserData.forEach(function(a) {
            // context variable here
            var key = a.id;
            var date = a.created;

            ann_occur[key] = {created: date};

            $http.get('/api/documents').success(function (data) {
                data.forEach(function(a) {
                    var title = a.title;
                    ann_occur[key].title = title;
                });
            });
        });
        $scope.ann_occur = ann_occur;
    });
}]);

neonionApp.controller('AnnDocsCtrl', ['$scope', '$http', '$location', function ($scope, $http, $location) {
    "use strict";
    var ann_docs = {};
    var docUri = [];
    var url = $location.absUrl().split('/');
    var quote = url[url.length-1];

    $http.get('/api/store/search?quote=' + quote).success(function (data) {
        var filterUserData = data.rows;

        filterUserData.forEach(function(a) {
            docUri.push(a.uri);
        });
    });

    $http.get('/api/documents/?format=json').success(function (data) {
        console.log(data);
        var urn = data.urn;
        var title = data.title;

        docUri.forEach(function(a) {
            if (!(urn in ann_docs) && urn == a) {
            ann_docs[urn] = {urn: urn, title: title};
        }
        });
    });

    $scope.ann_docs = ann_docs;
    console.log(ann_docs);
}]);

neonionApp.controller('AnnotatorCtrl', ['$scope', '$http', function ($scope, $http) {
    "use strict";

    $scope.setupAnnotator = function(uri, userId) {
        $("#document-body").annotator()
        .annotator('addPlugin', 'Neonion', {
            whoamiUrl: "/accounts/me"
        })
        .annotator('addPlugin', 'NER', {
            service : 'http://localhost:5000',
            uri : uri
        })
        .annotator('addPlugin', 'Store', {
            prefix: '/api/store',
            annotationData: {'uri': uri},
            // filter annotations by creator
            loadFromSearch: {
                'uri': uri,
                //'creator.email': userId,
                'limit': 999999
            }
        });

        $scope.annotator = $("#document-body").data("annotator");
        $scope.loadAnnotationSet();

        /*annotator.subscribe("annotationCreated", function (annotation) {
        notifyEndpoint(annotation);
        //annotationChanged(annotation);
        });*/

        // TODO raise refresh list when store plugin has finished async request
        /*window.setTimeout(function() {
        refreshContributors();
        var users = Annotator.Plugin.Neonion.prototype.getContributors();
        users.forEach(function(user) {
        var annotations = Annotator.Plugin.Neonion.prototype.getUserAnnotations(user);
        annotations.forEach(function(ann){
        colorizeAnnotation(ann);
        });
        });
        }, 1000);*/
    };

    $scope.loadAnnotationSet = function() {
        $http.get('/api/annotationsets').success(function (data) {
            $scope.annotationsets = data;
            if ($scope.annotationsets.length > 0) {
                var sets = {};
                $scope.annotationsets[0].concepts.forEach(function (item) {
                    if (item.uri == 'http://neonion.org/concept/person') {
                        sets[item.uri] = {
                            label: item.label,
                            create: Annotator.Plugin.Neonion.prototype.create.createPerson,
                            search: Annotator.Plugin.Neonion.prototype.search.searchPerson,
                            formatter: Annotator.Plugin.Neonion.prototype.formatter.formatPerson,
                            decorator: Annotator.Plugin.Neonion.prototype.decorator.decoratePerson
                        };
                    }
                    else if (item.uri == 'http://neonion.org/concept/institute') {
                        sets[item.uri] = {
                            label: item.label,
                            create: Annotator.Plugin.Neonion.prototype.create.createInstitute,
                            search: Annotator.Plugin.Neonion.prototype.search.searchInstitute,
                            formatter: Annotator.Plugin.Neonion.prototype.formatter.formatInstitute,
                            decorator: Annotator.Plugin.Neonion.prototype.decorator.decorateInstitute
                        };
                    }
                });

                $scope.annotator.plugins.Neonion.setCompositor(sets);
            }
        });
    };

}]);

neonionApp.controller('NamedEntityCtrl', ['$scope', '$http', function ($scope, $http) {
    "use strict";

    $scope.models = [
        {
            identifier: 'Standard',
            stanfordModel: 'dewac_175m_600',
            predictorNumberOfComponents: '?',
            predictorNumberOfIterations: '(10^6) / n',
            predictorLossFunction: 'log',
            predictorAlpha: '?',
            numberOfHiddenLayerComponents: 4,
            predictorInitialize: 'Standard',
            learnNetworkInitialize: 'Standard',
            predictorLearn: false,
            learnNetworkLearn: false
        }
    ];
}]);