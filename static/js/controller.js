var Hephaestus = angular.module('Hephaestus', [])

Hephaestus.controller('OnlineController', function($scope) {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/heph')
    
    $scope.users = [];
    $scope.username = '';
    $scope.currentPage = '';
    
    $scope.$watch('currentPage', function() {
        console.log("Updating user", $scope.currentPage, ' fuck');
        socket.emit('users', $scope.currentPage);
    });
    
    socket.on('connect', function() {
        console.log('connected');
    });
    
    socket.on('users', function(user) {
        
        console.log(user);
        $scope.users.push(user);
        $scope.$apply();
        
    });
    
/*
    $scope.newUser = function newUser() {
        console.log("Adding user", $scope.username);
        socket.emit('newUser', $scope.username);
    };
    
    
    $scope.updateUser = function updateUser() {
        console.log("Updating user", $scope.currentPage);
        socket.emit('users', $scope.currentPage);
    };
    
    $scope.getUsers = function getUsers() {
        socket.emit('users');
    };
*/
    $scope.activePage = function activePage() {
        console.log('In activePage');
    };
    
});