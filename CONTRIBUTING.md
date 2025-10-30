# Contributing to Tender Platform

Thank you for your interest in contributing to the Tender Platform! We welcome contributions from the community to help make this platform even better.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@your-domain.com](mailto:conduct@your-domain.com).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/your-org/tender-platform/issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps** which reproduce the problem in as many details as possible.
- **Provide specific examples** to demonstrate the steps.
- **Describe the behavior you observed** after following the steps.
- **Explain which behavior you expected** to see instead and why.
- **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem.
- **Include the version of the platform** you're using.
- **Include browser and OS information** if relevant.

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/your-org/tender-platform/issues). Create an issue and provide the following information:

- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description** of the suggested enhancement in as many details as possible.
- **Provide specific examples** to demonstrate the steps.
- **Describe the current behavior** and **explain which behavior you expected** to see instead.
- **Include screenshots and animated GIFs** which help you demonstrate the steps or point out the part of the platform which the suggestion is related to.
- **Explain why this enhancement would be useful** to most Tender Platform users.

### Code Contribution

#### Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/tender-platform.git
cd tender-platform
```

3. Create a branch for your feature or bugfix:
```bash
git checkout -b feature/your-feature-name
```

4. Set up the development environment:
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

5. Start development services:
```bash
cd ..
docker-compose up -d
```

#### Making Changes

1. **Follow the coding standards** outlined in the [Developer Guide](docs/DEVELOPER_GUIDE.md)
2. **Write tests** for your changes
3. **Update documentation** when needed
4. **Keep commits focused** on a single feature or bugfix
5. **Write clear commit messages** following [Conventional Commits](https://www.conventionalcommits.org/)

#### Commit Message Format

We follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to our CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files
- `revert`: Reverts a previous commit

Examples:
```
feat(auth): add OAuth2 authentication support

- Implement OAuth2 flow
- Add Google and GitHub login options
- Update user model with OAuth fields
```

```
fix(api): resolve tender search pagination issue

Fixes incorrect pagination calculation when filtering tenders
by multiple criteria. This resolves issue #123.

The problem was caused by counting total results before applying
filters, which led to incorrect page counts.
```

#### Testing Your Changes

Before submitting a pull request:

1. **Run the test suite**:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd ../frontend
npm test
```

2. **Check code formatting**:
```bash
# Backend
black --check .
isort --check-only .

# Frontend
npm run lint
```

3. **Verify documentation builds** (if you modified docs):
```bash
# Check that documentation compiles without errors
```

#### Submitting a Pull Request

1. **Ensure your branch is up to date**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Push your branch**:
```bash
git push origin feature/your-feature-name
```

3. **Create a Pull Request** through the GitHub interface:
   - Use a clear title following conventional commits
   - Provide a detailed description of your changes
   - Reference any related issues
   - Include screenshots if UI changes are involved

### Pull Request Process

1. **Automated Checks**: CI pipeline runs tests, linting, and security checks
2. **Code Review**: Maintainers review the code for quality, security, and adherence to standards
3. **Security Review**: Security-sensitive changes receive extra scrutiny
4. **Documentation Review**: Documentation updates are verified
5. **Merge**: Approved PRs are merged to the main branch

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Styleguide

Follow [PEP 8](https://pep8.org/) with these additions:

- Use Black for code formatting
- Use isort for import organization
- Use type hints for all functions and classes
- Use Google-style docstrings
- Maximum line length: 88 characters (Black default)

### JavaScript/TypeScript Styleguide

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use Prettier for code formatting
- Use ESLint for linting
- Use TypeScript for type safety

### CSS Styleguide

- Use SCSS for styling
- Follow [BEM methodology](http://getbem.com/)
- Use meaningful class names
- Organize styles by component

## Community

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general discussion and questions
- **Discord**: Real-time chat with other contributors (link in README)
- **Email**: For sensitive topics [contributors@your-domain.com](mailto:contributors@your-domain.com)

### Recognition

We appreciate all contributions, big and small. Contributors are recognized in:

- [README.md](README.md) contributor list
- Release notes for each version
- Social media shoutouts for significant contributions

## Questions?

If you have any questions about contributing, feel free to:

1. Open an issue with your question
2. Join our Discord community
3. Email [contributors@your-domain.com](mailto:contributors@your-domain.com)

Thank you for contributing to the Tender Platform!