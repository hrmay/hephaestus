var Hephaestus = angular.module('Hephaestus', [])

Hephaestus.controller('OnlineController', function($scope) {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/heph')
    
    $scope.users = [];
    $scope.currentPage = '';
    
    socket.on('connect', function() {
        console.log('connected');
    });
    
    socket.on('users', function(user) {
        console.log(user);
        $scope.users.push(user);
        $scope.$apply();
    });
    
    $scope.activePage = function activePage() {
        console.log('In activePage');
    };
    
});