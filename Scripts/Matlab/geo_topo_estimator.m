n = 8;                          % Number of points
dim = 10;                       % Size of the space.
X_true = rand(n-1, 2) * dim;    % True positions of points
X_true = [0 0; 0 X_true(1, 2); X_true(2:end, :)];
cutoff_dist = 10;              % Having a measurement above this distance would be unrealistic.
sensor_error = 0.1;             % Percentage error of distance readings.

% Generate random measurements.
Y = zeros(n);
for i=1:n
    for j=1:n
        if (i ~= j)
            d = norm(X_true(i,:) - X_true(j,:));
            if d <= cutoff_dist
                Y(i, j) = max(d + normrnd(0, sensor_error / 3), 0);
            end
        end
    end
end

Y

%% Find the results with the optimization.
x0 = zeros(1, 2*n - 3);
fun = @(x)objective(x, Y);
options = optimset('Display', 'iter');
[sol, mse1] = fmincon(fun, x0, [], [], [], [], 0, Inf, [], options);
X_est = [0 0; 0 sol(1); reshape(sol(2:end), 2, [])']
mse1


%% Plot the results
figure(1)
scatter(X_true(:, 1), X_true(:, 2), 100, 'red', 's')
hold on
scatter(X_est(:, 1), X_est(:, 2), 100, 'blue', 'x')
hold off
grid();
% xlim([-1, dim+1])
% ylim([-1, dim+1])


%% Define objective function

% objective(sol, Y)

function mse=objective(x, Y)
n = size(Y, 1);
X = [0 0; 0 x(1)];
X = [X; reshape(x(2:end), 2, [])'];


mse = 0;
c = 0;
for i=1:n
    for j=1:n
        if (i ~= j)
            d = norm(X(i,:) - X(j,:));
            if Y(i,j) > 0
                mse = mse + (d - Y(i, j)) .^ 2;
                c = c + 1;
            end
        end
    end
end
mse = mse / c;

end