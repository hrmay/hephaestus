var Hephaestus = angular.module('Hephaestus', [])

Hephaestus.controller('OnlineController', function($scope) {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/heph')
    
    $scope.usersOnline = [];
    $scope.currentPage = '';
    
    socket.on('connect', function() {
        console.log('connected');
    });
    
    $scope.activePage = function activePage() {
        console.log('In activePage');
    };
    
});